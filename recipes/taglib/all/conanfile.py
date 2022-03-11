from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class TaglibConan(ConanFile):
    name = "taglib"
    description = "TagLib is a library for reading and editing the metadata of several popular audio formats."
    license = ("LGPL-2.1-or-later", "MPL-1.1")
    topics = ("conan", "taglib", "audio", "metadata")
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

    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_CCACHE"] = False
        self._cmake.definitions["VISIBILITY_HIDDEN"] = True
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_BINDINGS"] = self.options.bindings
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING.*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "taglib-config")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "taglib_full_package" # unofficial, to avoid conflicts in pkg_config generator

        self.cpp_info.components["tag"].names["pkg_config"] = "taglib"
        self.cpp_info.components["tag"].includedirs.append(os.path.join("include", "taglib"))
        self.cpp_info.components["tag"].libs = ["tag"]
        self.cpp_info.components["tag"].requires = ["zlib::zlib"]
        if not self.options.shared:
            self.cpp_info.components["tag"].defines.append("TAGLIB_STATIC")

        if self.options.bindings:
            self.cpp_info.components["tag_c"].names["pkg_config"] = "taglib_c"
            self.cpp_info.components["tag_c"].libs = ["tag_c"]
            self.cpp_info.components["tag_c"].requires = ["tag"]
            if not self.options.shared:
                libcxx = tools.stdcpp_library(self)
                if libcxx:
                    self.cpp_info.components["tag"].system_libs.append(libcxx)
