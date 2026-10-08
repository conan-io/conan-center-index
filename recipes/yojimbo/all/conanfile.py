import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=2.19.0"


class YojimboConan(ConanFile):
    name = "yojimbo"
    description = "A network library for client/server games written in C++"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mas-bandwidth/yojimbo"
    topics = ("game", "udp", "protocol", "client-server", "multiplayer-game-server")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def requirements(self):
        self.requires("libsodium/[~1.0.20]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["YOJIMBO_SYSTEM_SODIUM"] = True
        tc.cache_variables["YOJIMBO_SYSTEM_DEPS"] = False
        tc.cache_variables["YOJIMBO_BUILD_TESTS"] = False
        tc.cache_variables["YOJIMBO_INSTALL"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENCE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "yojimbo")
        self.cpp_info.set_property("cmake_target_name", "Yojimbo::yojimbo")
        self.cpp_info.libs = ["yojimbo"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "iphlpapi"]
