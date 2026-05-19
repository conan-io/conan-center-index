from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=2.0"


class SablibConan(ConanFile):
    name = "sablib"
    description = "Signal smoothing and baseline estimation library for C++"
    license = "MIT"
    homepage = "https://izadori.net/"
    url = "https://github.com/Izadori/sablib"
    topics = ("signal-processing", "baseline", "smoothing", "eigen")
    package_type = "static-library"
    settings = "os", "compiler", "build_type", "arch"

    def set_version(self):
        self.version = self.conan_data["version"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["sablib"]
