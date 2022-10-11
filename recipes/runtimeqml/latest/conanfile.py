import os

from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir

required_conan_version = ">=1.49.0"


class RuntimeQml(ConanFile):
    name = "runtimeqml"
    homepage = "https://github.com/GIPdA/runtimeqml"
    description = "Enables hot-reloading qml files"
    topics = ("qt", "hot-reload", "qml", "gui")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    generators = "CMakeDeps", "CMakeToolchain"

    def export_sources(self):
        self.copy("CMakeLists.txt", dst="src")

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)],
            destination=self.source_folder, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("qt/[>=6.0.0]")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        self.options["qt"].shared = True
        self.options["qt"].qtdeclarative = True
        self.options["qt"].qtshadertools = True
        self.options["qt"].with_libjpeg = "libjpeg-turbo"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", src=self.source_folder, dst="licenses")
        self.copy(pattern="*.lib", dst="lib")
        self.copy(pattern="*.dylib", dst="lib")
        self.copy(pattern="*.so", dst="lib")
        self.copy(pattern="*.dll", dst="bin")
        self.copy(pattern="*.hpp", src=self.source_folder, dst="include")
