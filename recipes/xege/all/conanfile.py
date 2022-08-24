from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class XegeConan(ConanFile):
    name = "xege"
    license = "LGPLv2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://xege.org/"
    description = "Easy Graphics Engine, a lite graphics library in Windows"
    topics = ("ege", "graphics", "gui")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]

    def configure(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration(
                "This library is only compatible for Windows")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("*.h", dst="include", src=self._source_subfolder+"/src")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        if self.settings.arch == "x86_64":
            self.cpp_info.libs = ["graphics64"]
        else:
            self.cpp_info.libs = ["graphics"]
        self.cpp_info.system_libs = [
            "gdiplus",
            "uuid",
            "msimg32",
            "gdi32",
            "imm32",
            "ole32",
            "oleaut32"
        ]
