from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=1.53.0"


class UnityConan(ConanFile):
    name = "unity"
    description = "Unity Test is a unit testing framework built for C, with a focus on working with embedded toolchains"
    topics = ("unit-test", "tdd", "bdd", "testing")
    license = "MIT"
    homepage = "http://www.throwtheswitch.org"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "fixture_extension": [True, False],
        "memory_extension": [True, False],
    }
    default_options = {
        "fPIC": True,
        "fixture_extension": False,
        "memory_extension": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["UNITY_EXTENSION_FIXTURE"] = self.options.fixture_extension
        tc.cache_variables["UNITY_EXTENSION_MEMORY"] = self.options.memory_extension
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["unity"]
        self.cpp_info.includedirs = ["include", "include/unity"]
