from os import path

from conan import ConanFile
from conan.tools.build.cppstd import check_min_cppstd
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import get, copy

required_conan_version = ">=1.47.0"


class SamariumConan(ConanFile):
    name = "samarium"
    version = "1.0.1"
    description = "2-D physics simulation library"
    homepage = "https://strangequark1041.github.io/samarium/"
    url = "https://github.com/conan-io/conan-center-index/"
    license = "MIT"
    topics = ("cpp20", "physics", "2d", "simulation")
    generators = "CMakeDeps", "CMakeToolchain"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [
        True, False], "build_tests": [True, False]}
    default_options = {"shared": False, "fPIC": True, "build_tests": False}

    def source(self):
        get(self, **self.conan_data["sources"]
            [str(self.version)], strip_root=True)

    def requirements(self):
        self.requires("fmt/9.0.0")
        self.requires("sfml/2.5.1")
        self.requires("range-v3/0.12.0")
        self.requires("stb/cci.20210910")

        if self.options.build_tests:
            self.requires('catch2/3.0.1')
            self.requires('benchmark/1.6.1')

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "20")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="src")
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.folders.source_folder,
             dst=path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["samarium"]
