from conan import ConanFile, tools
from conans import CMake
from conans.tools import os_info
import os


class libuiConan(ConanFile):
    name = "libui"
    description = "Simple and portable GUI library in C that uses the native GUI technologies of each platform it supports."
    topics = ("conan", "libui", "ui", "gui")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/andlabs/libui"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "pkg_config"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        self.requires("gtk/3.24.24")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=self._source_subfolder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self, self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(
                [
                    "user32",
                    "kernel32",
                    "gdi32",
                    "comctl32",
                    "msimg32",
                    "comdlg32",
                    "d2d1",
                    "dwrite",
                    "ole32",
                    "oleaut32",
                    "oleacc",
                    "uuid",
                    "windowscodecs",
                ]
            )
