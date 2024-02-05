import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import stdcpp_library, check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.54.0"


class TaglibConan(ConanFile):
    name = "taglib"
    description = "TagLib is a library for reading and editing the metadata of several popular audio formats."
    license = ("LGPL-2.1-or-later", "MPL-1.1")
    topics = ("audio", "metadata")
    homepage = "https://taglib.org"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "bindings": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "bindings": True,
    }

    @property
    def _min_cppstd(self):
        # https://github.com/taglib/taglib/blob/v2.0beta/CMakeLists.txt#L5
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        if Version(self.version) >= 2:
            self.requires("utfcpp/4.0.4")

    def validate(self):
        if Version(self.version) >= 2:
            if self.settings.compiler.cppstd:
                check_min_cppstd(self, self._min_cppstd)
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_CCACHE"] = False
        tc.variables["VISIBILITY_HIDDEN"] = True
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_BINDINGS"] = self.options.bindings
        tc.variables["ENABLE_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # relocatable shared libs on macOS
        for cmakelists in [
            os.path.join(self.source_folder, "taglib", "CMakeLists.txt"),
            os.path.join(self.source_folder, "bindings", "c", "CMakeLists.txt"),
        ]:
            replace_in_file(self, cmakelists, "INSTALL_NAME_DIR ${", "# INSTALL_NAME_DIR ${")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING.*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "taglib-config", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "taglib_full_package") # unofficial, to avoid conflicts in pkg_config generator

        self.cpp_info.components["tag"].set_property("pkg_config_name", "taglib")
        self.cpp_info.components["tag"].includedirs.append(os.path.join("include", "taglib"))
        self.cpp_info.components["tag"].libs = ["tag"]
        self.cpp_info.components["tag"].requires = ["zlib::zlib"]
        if Version(self.version) >= 2:
            self.cpp_info.components["tag"].requires.append("utfcpp::utfcpp")
        if not self.options.shared:
            self.cpp_info.components["tag"].defines.append("TAGLIB_STATIC")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["tag"].system_libs.append("m")

        if self.options.bindings:
            self.cpp_info.components["tag_c"].set_property("pkg_config_name", "taglib_c")
            self.cpp_info.components["tag_c"].libs = ["tag_c"]
            self.cpp_info.components["tag_c"].requires = ["tag"]
            if not self.options.shared:
                libcxx = stdcpp_library(self)
                if libcxx:
                    self.cpp_info.components["tag"].system_libs.append(libcxx)
