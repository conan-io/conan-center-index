from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rm, rmdir
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.50.0"


class TaglibConan(ConanFile):
    name = "taglib"
    description = "TagLib is a library for reading and editing the metadata of several popular audio formats."
    license = ("LGPL-2.1-or-later", "MPL-1.1")
    topics = ("taglib", "audio", "metadata")
    homepage = "https://taglib.org"
    url = "https://github.com/conan-io/conan-center-index"

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

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.12")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_CCACHE"] = False
        tc.variables["VISIBILITY_HIDDEN"] = True
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_BINDINGS"] = self.options.bindings
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
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
            replace_in_file(self, cmakelists, "INSTALL_NAME_DIR ${LIB_INSTALL_DIR}", "")

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
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "taglib_full_package") # unofficial, to avoid conflicts in pkg_config generator

        self.cpp_info.components["tag"].set_property("pkg_config_name", "taglib")
        self.cpp_info.components["tag"].includedirs.append(os.path.join("include", "taglib"))
        self.cpp_info.components["tag"].libs = ["tag"]
        self.cpp_info.components["tag"].requires = ["zlib::zlib"]
        if not self.options.shared:
            self.cpp_info.components["tag"].defines.append("TAGLIB_STATIC")

        if self.options.bindings:
            self.cpp_info.components["tag_c"].set_property("pkg_config_name", "taglib_c")
            self.cpp_info.components["tag_c"].libs = ["tag_c"]
            self.cpp_info.components["tag_c"].requires = ["tag"]
            if not self.options.shared:
                libcxx = tools_legacy.stdcpp_library(self)
                if libcxx:
                    self.cpp_info.components["tag"].system_libs.append(libcxx)
