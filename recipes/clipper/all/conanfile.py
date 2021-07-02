import os
from conans import ConanFile, CMake, tools


class ClipperConan(ConanFile):
    name = "clipper"
    description = """Clipper is an open source freeware polygon clipping library"""
    topics = ("conan", "clipper")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/skyrpex/clipper"
    license = "BSL-1.0"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "arch", "build_type", "compiler", "os"
    _cmake = None
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {"shared": False, "fPIC": True}

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        if "patches" in self.conan_data and self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("License.txt", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "polyclipping"
        self.cpp_info.names["cmake_find_package_multi"] = "polyclipping"
        self.cpp_info.names["pkg_config"] = "polyclipping"
        self.cpp_info.libs = ["polyclipping"]
