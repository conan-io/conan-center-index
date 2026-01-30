import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, get

class SockppConan(ConanFile):
    name = "sockpp"
    package_type = "library"

    # Optional metadata
    license = "BSD 3-Clause"
    url = "https://github.com/fpagliughi/sockpp"
    description = "Modern C++ socket library."
    topics = ("sockets", "networking", "cpp")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]
    languages = "C++"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)


    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["SOCKPP_BUILD_SHARED"] = self.options.shared
        tc.variables["SOCKPP_BUILD_STATIC"] = not self.options.shared
        tc.variables["SOCKPP_WITH_UNIX_SOCKETS"] = self.options.with_unix_sockets
        if self.settings.os == "Linux":
            tc.variables["SOCKPP_WITH_CAN"] = self.options.with_can
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))


    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["sockpp" if self.options.shared else "sockpp-static"]
            self.cpp_info.system_libs = ["ws2_32"]
        else:
            self.cpp_info.libs = ["sockpp"]


