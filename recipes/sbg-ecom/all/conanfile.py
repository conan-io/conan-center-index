from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

import os

required_conan_version = ">=2.1"


class SbgEComConan(ConanFile):
    name = "sbgecom"
    license = "MIT"
    author = "Alexandre Petitjean <alexandre.petitjean@sbg-systems.com>"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/SBG-Systems/sbgECom"
    description = "C library used to communicate with SBG Systems IMU, AHRS and INS"
    topics = ("sbg", "imu", "ahrs", "ins")
    
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self)
    
    def validate(self):
        check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["sbgECom"]
