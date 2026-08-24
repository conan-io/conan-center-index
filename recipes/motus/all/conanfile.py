# Conan recipe for motus, shaped for a conan-center-index submission
# (recipes/motus/all/conanfile.py there; see SUBMITTING.md beside this file).

import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir


class MotusConan(ConanFile):
    name = "motus"
    description = (
        "Transport-agnostic messaging seam for C++17 with a per-backend "
        "conformance suite and a Windows-safe AMQP-CPP connection handler"
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mertefesensoy/motus"
    topics = ("messaging", "amqp", "rabbitmq", "transport", "cpp17")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_amqpcpp": [True, False],
        "with_inmemory": [True, False],
    }
    default_options = {
        "with_amqpcpp": True,
        "with_inmemory": True,
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_amqpcpp:
            self.requires("amqp-cpp/4.3.27")
            self.requires("boost/[>=1.81 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MOTUS_BUILD_TESTS"] = False
        tc.variables["MOTUS_WITH_AMQPCPP"] = bool(self.options.with_amqpcpp)
        tc.variables["MOTUS_WITH_INMEMORY"] = bool(self.options.with_inmemory)
        tc.variables["MOTUS_WITH_SIMPLEAMQP"] = False
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["motus"]
        self.cpp_info.set_property("cmake_file_name", "motus")
        self.cpp_info.set_property("cmake_target_name", "motus::motus")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
