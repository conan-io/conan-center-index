# Conan recipe for motus, shaped for a conan-center-index submission
# (recipes/motus/all/conanfile.py there; see SUBMITTING.md beside this file).

import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=2.0.9"


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
    # Upstream CMakeLists.txt declares add_library(motus STATIC ...) unconditionally,
    # so there is no shared build to expose and hence no "shared" option.
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_amqpcpp": [True, False],
        "with_inmemory": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_amqpcpp": True,
        "with_inmemory": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_amqpcpp:
            # transitive_headers because both are reachable from INSTALLED public headers:
            # INFO: <amqpcpp.h> in motus/AmqpConnection.hpp:20 and
            #       motus/transport/backends/AmqpCppTransport.hpp:14
            # INFO: <boost/asio/*.hpp> in motus/AmqpConnection.hpp:14-18
            self.requires("amqp-cpp/4.3.27", transitive_headers=True)
            self.requires("boost/1.88.0", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 17)
        if not self.options.with_amqpcpp and not self.options.with_inmemory:
            # Upstream turns this into a configure-time FATAL_ERROR; fail earlier and
            # with a message that names the Conan options rather than the CMake ones.
            raise ConanInvalidConfiguration(
                f"{self.ref} requires at least one transport backend: enable "
                "-o with_amqpcpp=True and/or -o with_inmemory=True."
            )

    def build_requirements(self):
        # Upstream sets cmake_minimum_required(VERSION 3.21); ConanCenter only
        # guarantees 3.15 on the build machine.
        self.tool_requires("cmake/[>=3.21]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["MOTUS_BUILD_TESTS"] = False
        tc.cache_variables["MOTUS_WITH_AMQPCPP"] = bool(self.options.with_amqpcpp)
        tc.cache_variables["MOTUS_WITH_INMEMORY"] = bool(self.options.with_inmemory)
        tc.cache_variables["MOTUS_WITH_SIMPLEAMQP"] = False
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
            # Mirrors the PUBLIC link libraries and compile definitions upstream puts on
            # the motus target. They cannot be inherited here: the exported
            # motusTargets.cmake that carried them is removed in package(), so CMakeDeps
            # generates the config file and the recipe has to restate the interface.
            # mswsock is Boost.Asio's Windows requirement alongside ws2_32, and
            # _WIN32_WINNT must be defined before any consumer translation unit pulls in
            # a Boost.Asio header through motus/AmqpConnection.hpp.
            self.cpp_info.system_libs = ["ws2_32", "mswsock"]
            self.cpp_info.defines = ["_WIN32_WINNT=0x0601", "WIN32_LEAN_AND_MEAN"]
