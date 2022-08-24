from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.36.0"


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

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.12")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # relocatable shared libs on macOS
        for cmakelists in [
            os.path.join(self._source_subfolder, "taglib", "CMakeLists.txt"),
            os.path.join(self._source_subfolder, "bindings", "c", "CMakeLists.txt"),
        ]:
            tools.files.replace_in_file(self, cmakelists, "INSTALL_NAME_DIR ${LIB_INSTALL_DIR}", "")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_CCACHE"] = False
        cmake.definitions["VISIBILITY_HIDDEN"] = True
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_BINDINGS"] = self.options.bindings
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING.*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rm(self, os.path.join(self.package_folder, "bin"), "taglib-config")
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

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
                libcxx = tools.stdcpp_library(self)
                if libcxx:
                    self.cpp_info.components["tag"].system_libs.append(libcxx)
