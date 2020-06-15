import os
from os import path
from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration


class ClipperConan(ConanFile):
    name = "clipper"
    description = """Clipper is an open source freeware polygon clipping library"""
    topics = ("conan", "clipper")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/skyrpex/clipper"
    license = "BSL-1.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "arch", "build_type", "compiler", "os"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
        }
    default_options = {"shared": False, "fPIC": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder, source_folder=os.path.join(self._source_subfolder, "cpp"))
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("License.txt", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["polyclipping"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append('pthread')
