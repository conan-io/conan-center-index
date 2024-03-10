import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout, CMakeDeps, CMakeToolchain
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=1.52.0"


class CNatsConan(ConanFile):
    name = "cnats"
    description = "A C Client for NATS"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nats-io/nats.c"
    topics = ("messaging", "message-bus", "message-queue", "messaging-library", "nats-client")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
    
    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")
        self.requires("protobuf-c/1.5.0")
        # TODO: Not actually transitive headers, and not a direct dependency.
        # Unsure why, but without this the protobuf CMake config file (required from
        # protobuf-c) isn't generated. This is also only necessary in shared mode.
        if self.options.shared:
            self.requires("protobuf/3.21.9", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NATS_BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.variables["NATS_BUILD_LIB_STATIC"] = not self.options.shared
        tc.variables["NATS_BUILD_LIB_SHARED"] = self.options.shared
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        suffix = "" if self.options.shared else "_static"
        self.cpp_info.libs = [f"nats{suffix}"]
        self.cpp_info.set_property("cmake_target_name", f"cnats::nats{suffix}")
