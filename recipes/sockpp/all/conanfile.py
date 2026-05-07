import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=2.4"

class SockppConan(ConanFile):
    name = "sockpp"
    package_type = "library"
    license = "BSD-3-Clause"
    homepage = "https://github.com/fpagliughi/sockpp"
    url = "https://github.com/conan-io/conan-center-index"
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
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SOCKPP_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["SOCKPP_BUILD_STATIC"] = not self.options.shared
        tc.generate()

    def validate(self):
        check_min_cppstd(self, 14)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "Sockpp::sockpp" if self.options.shared else "Sockpp::sockpp-static")
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["sockpp" if self.options.shared else "sockpp-static"]
            self.cpp_info.system_libs = ["ws2_32"]
        else:
            self.cpp_info.libs = ["sockpp"]


