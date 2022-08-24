from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
import os

class NinjaConan(ConanFile):
    name = "ninja"
    description = "Ninja is a small build system with a focus on speed"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ninja-build/ninja"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt", "*.patch"]
    generators = "cmake"
    topics = ("conan", "ninja", "build")

    _source_subfolder = "source_subfolder"
    _cmake = None

    def package_id(self):
        del self.info.settings.compiler

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = "OFF"
        self._cmake.configure()
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ninja-%s" % self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.includedirs = []
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.CONAN_CMAKE_GENERATOR = "Ninja"
