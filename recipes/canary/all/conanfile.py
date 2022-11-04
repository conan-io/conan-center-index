import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=1.53.0"


class SocketcanCanaryConan(ConanFile):
    name = "canary"
    description = "A lightweight implementation of Linux SocketCAN bindings for ASIO/Boost.ASIO"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0 license"
    homepage = "https://github.com/djarek/canary"
    topics = ("socketcan", "canary")

    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    def requirements(self):
        self.requires("boost/1.74.0", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE_1_0.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.requires = ["boost::headers"]
        self.cpp_info.set_property("cmake_file_name", "canary")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_target_name", "canary::canary")
