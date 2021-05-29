import os
from conans import ConanFile, CMake, tools


class Chipmunk2DConan(ConanFile):
    name = "chipmunk2d"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/slembcke/Chipmunk2D"
    topics = ("physics", "engine", "game development")
    description = "Chipmunk2D is a simple, lightweight, fast and portable 2D "\
                  "rigid body physics library written in C."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False, 
        "fPIC": True
    }
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "Chipmunk2D-Chipmunk-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_DEMOS"] = False
        self._cmake.definitions["INSTALL_DEMOS"] = False
        self._cmake.definitions["INSTALL_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        chipmunk_name = "chipmunk" if self.options.shared else "chipmunk_static"
        self.cpp_info.components["chipmunk"].names["cmake_find_package"] = chipmunk_name
        self.cpp_info.components["chipmunk"].names["cmake_find_package_multi"] = chipmunk_name
        self.cpp_info.components["chipmunk"].libs = ["chipmunk"]
        if self.settings.os == "Linux":
            self.cpp_info.components["chipmunk"].system_libs = ["m", "pthread"]
