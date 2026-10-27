from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, check_min_vs
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"


class Exiv2Conan(ConanFile):
    name = "exiv2"
    description = "Exiv2 is a C++ library and a command-line utility " \
                  "to read, write, delete and modify Exif, IPTC, XMP and ICC image metadata."
    license = "GPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.exiv2.org"
    topics = ("image", "exif", "xmp")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_xmp": [False, "bundled", "external"],
        "with_curl": [True, False],
        "with_brotli": [True, False],
        "with_inih": [True, False],
        "win_unicode": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": True,
        "with_xmp": "bundled",
        "with_curl": False,
        "with_brotli": True,
        "with_inih": True,
        "win_unicode": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.win_unicode
        else:
            del self.options.with_brotli
            del self.options.with_inih

            if self.settings.os == "Windows":
                self.options.win_unicode = True

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.with_xmp == "bundled":
            # recipe has bundled xmp-toolkit-sdk of old version
            # avoid conflict with a future xmp recipe
            self.provides = ["xmp-toolkit-sdk"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os != "Windows":
            self.requires("libiconv/1.17")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_xmp == "bundled":
            self.requires("expat/[>=2.6.2 <3]")
        if self.options.with_curl:
            self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.get_safe("with_brotli"):
            self.requires("brotli/[>=1.1.1 <2]")
        if self.options.get_safe("with_inih"):
            self.requires("inih/58")

    def validate(self):
        min_cppstd = 17

        check_min_cppstd(self, min_cppstd)
        check_min_vs(self, 191)

        compilers_minimum_version = {
            "gcc": "8",
            "clang": "5",
            "apple-clang": "10",
        }
        minimum_version = compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{min_cppstd}, which your compiler does not fully support."
            )

        if self.options.with_xmp == "external":
            raise ConanInvalidConfiguration("adobe-xmp-toolkit is not available on cci (yet)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["EXIV2_BUILD_SAMPLES"] = False
        tc.variables["EXIV2_BUILD_EXIV2_COMMAND"] = False
        tc.variables["EXIV2_ENABLE_PNG"] = self.options.with_png
        tc.variables["EXIV2_ENABLE_XMP"] = self.options.with_xmp == "bundled"
        tc.variables["EXIV2_ENABLE_EXTERNAL_XMP"] = self.options.with_xmp == "external"
        # NLS is used only for tool which is not built
        tc.variables["EXIV2_ENABLE_NLS"] = False
        tc.variables["EXIV2_ENABLE_WEBREADY"] = self.options.with_curl
        tc.variables["EXIV2_ENABLE_CURL"] = self.options.with_curl
        tc.variables["EXIV2_ENABLE_SSH"] = False
        tc.variables["EXIV2_ENABLE_BMFF"] = self.options.with_brotli
        tc.variables["EXIV2_ENABLE_BROTLI"] = self.options.with_brotli
        tc.variables["EXIV2_ENABLE_INIH"] = self.options.with_inih
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"

        if is_msvc(self):
            tc.variables["EXIV2_ENABLE_DYNAMIC_RUNTIME"] = not is_msvc_static_runtime(self)
        # set PIC manually because of the internal static library exiv2_int
        tc.cache_variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.get_safe("fPIC", True))
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                        "POSITION_INDEPENDENT_CODE ON", "")
        # Enforce usage of FindEXPAT.cmake
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "findDependencies.cmake"),
                        "find_package(EXPAT REQUIRED)", "find_package(EXPAT REQUIRED MODULE)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "exiv2")
        self.cpp_info.set_property("pkg_config_name", "exiv2")

        # component exiv2lib
        self.cpp_info.components["exiv2lib"].set_property("cmake_target_name", "exiv2lib")
        self.cpp_info.components["exiv2lib"].libs = ["exiv2"]
        if self.settings.os != "Windows":
            self.cpp_info.components["exiv2lib"].requires = [ "libiconv::libiconv"]
        if self.options.with_png:
            self.cpp_info.components["exiv2lib"].requires.extend(["libpng::libpng", "zlib::zlib"])
        if self.options.with_curl:
            self.cpp_info.components["exiv2lib"].requires.append("libcurl::libcurl")
        if self.options.get_safe("with_brotli"):
            self.cpp_info.components["exiv2lib"].requires.extend(["brotli::brotlidec", "brotli::brotlienc"])
        if self.options.get_safe("with_inih"):
            self.cpp_info.components["exiv2lib"].requires.append("inih::inireader")

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["exiv2lib"].system_libs.extend(["pthread"])
        if self.settings.os == "Windows":
            self.cpp_info.components["exiv2lib"].system_libs.extend(["psapi", "ws2_32"])
            self.cpp_info.components["exiv2lib"].defines.append("WIN32_LEAN_AND_MEAN")

        # component exiv2-xmp
        if self.options.with_xmp == "bundled":
            self.cpp_info.components["exiv2lib"].requires.append("expat::expat")
