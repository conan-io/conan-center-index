import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class SocketcanCanaryConan(ConanFile):
    name = "canary"
    description = "A lightweight implementation of Linux SocketCAN bindings for ASIO/Boost.ASIO"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0"
    homepage = "https://github.com/djarek/canary"
    topics = ("socketcan", "can-bus", "can")
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/[>=1.74.0 <=1.89.0]")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux.")
        
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        if Version(self.dependencies["boost"].ref.version) >= "1.89.0":
            deps.set_property("boost::headers", "cmake_target_aliases", ["Boost::system"])
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE_1_0.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.requires = ["boost::headers"]
        self.cpp_info.set_property("cmake_file_name", "canary")
        self.cpp_info.set_property("cmake_target_name", "canary::canary")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
