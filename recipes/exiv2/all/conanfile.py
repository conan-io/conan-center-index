from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir, save, export_conandata_patches, apply_conandata_patches, replace_in_file
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, check_min_vs
from conan.tools.scm import Version
import os
import sys
import textwrap

required_conan_version = ">=1.53.0"


class Exiv2Conan(ConanFile):
    name = "exiv2"
    description = "Exiv2 is a C++ library and a command-line utility " \
                  "to read, write, delete and modify Exif, IPTC, XMP and ICC image metadata."
    license = "GPL-2.0"
    topics = ("image", "exif", "xmp")
    homepage = "https://www.exiv2.org"
    url = "https://github.com/conan-io/conan-center-index"

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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) >= "0.28.0":
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
        self.requires("libiconv/1.17")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_xmp == "bundled":
            self.requires("expat/2.5.0")
        if self.options.with_curl:
            self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.get_safe("with_brotli"):
            self.requires("brotli/1.1.0")
        if self.options.get_safe("with_inih"):
            self.requires("inih/57")

    def validate(self):
        if Version(self.version) >= "0.28.0":
            min_cppstd = 17

            if self.settings.compiler.cppstd:
                check_min_cppstd(self, min_cppstd)
            check_min_vs(self, 191)

            compilers_minimum_version = {
                "gcc": "8",
                "clang": "5",
                "apple-clang": "10",
            }
            if not is_msvc(self):
                minimum_version = compilers_minimum_version.get(str(self.settings.compiler), False)
                if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
                    raise ConanInvalidConfiguration(
                        f"{self.ref} requires C++{min_cppstd}, which your compiler does not fully support."
                    )
        elif conan_version.major == 2:
            # FIXME: linter complains, but function is there
            # https://docs.conan.io/2.0/reference/tools/build.html?highlight=check_min_cppstd#conan-tools-build-check-max-cppstd
            check_max_cppstd = getattr(sys.modules['conan.tools.build'], 'check_max_cppstd')
            # https://github.com/Exiv2/exiv2/tree/v0.27.7#217-building-with-c11-and-other-compilers
            check_max_cppstd(self, 14)

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
        if Version(self.version) >= "0.28.0":
            tc.variables["EXIV2_ENABLE_BMFF"] = self.options.with_brotli
            tc.variables["EXIV2_ENABLE_BROTLI"] = self.options.with_brotli
            tc.variables["EXIV2_ENABLE_INIH"] = self.options.with_inih
        else:
            tc.variables["EXIV2_ENABLE_WIN_UNICODE"] = self.options.win_unicode
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"

        if is_msvc(self):
            tc.variables["EXIV2_ENABLE_DYNAMIC_RUNTIME"] = not is_msvc_static_runtime(self)
        # set PIC manually because of the internal static library exiv2_int
        tc.cache_variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.get_safe("fPIC", True))
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
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

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        targets = {"exiv2lib": "exiv2::exiv2lib"}
        if self.options.with_xmp == "bundled":
            targets.update({"exiv2-xmp": "exiv2::exiv2-xmp"})
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            targets
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "exiv2")
        self.cpp_info.set_property("pkg_config_name", "exiv2")

        # component exiv2lib
        self.cpp_info.components["exiv2lib"].set_property("cmake_target_name", "exiv2lib")
        self.cpp_info.components["exiv2lib"].libs = ["exiv2"]
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
            if Version(self.version) < "0.28.0":
                self.cpp_info.components["exiv2-xmp"].set_property("cmake_target_name", "exiv2-xmp")
                self.cpp_info.components["exiv2-xmp"].libs = ["exiv2-xmp"]
                self.cpp_info.components["exiv2-xmp"].requires = [ "expat::expat" ]
                self.cpp_info.components["exiv2lib"].requires.append("exiv2-xmp")
            else:
                self.cpp_info.components["exiv2lib"].requires.append("expat::expat")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["exiv2lib"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["exiv2lib"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if self.options.with_xmp == "bundled" and Version(self.version) < "0.28.0":
            self.cpp_info.components["exiv2-xmp"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["exiv2-xmp"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
