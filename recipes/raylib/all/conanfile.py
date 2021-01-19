import os
from conans import ConanFile, CMake, tools

class RaylibConan(ConanFile):
    name = "raylib"
    description = "raylib is a simple and easy-to-use library to enjoy videogames programming."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.raylib.com/"
    topics = ("conan", "raylib", "gamedev")

    settings = "os", "arch", "compiler", "build_type"
    options = { "shared": [True, False], "fPIC": [True, False] }
    default_options = { "shared": False, "fPIC": True }

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("opengl/system")
        if self.settings.os == "Linux":
            self.requires("xorg/system")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "raylib"
        self.cpp_info.names["cmake_find_package_multi"] = "raylib"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m", "pthread", "dl", "rt"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["gdi32", "winmm"])
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["Cocoa", "IOKit", "CoreVideo"])
