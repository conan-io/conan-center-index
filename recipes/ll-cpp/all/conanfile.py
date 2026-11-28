import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=2.0"


class LlCppConan(ConanFile):
    name = "ll-cpp"
    description = "Language-only C++17 Telegram bot runtime"
    license = "MIT"
    homepage = "https://github.com/ll-tg/ll-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("telegram", "telegram-bot", "bot", "runtime")
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", False)
        tc.variables["LLCPP_BUILD_RUNTIME"] = False
        tc.variables["LLCPP_BUILD_EXAMPLES"] = False
        tc.variables["LLCPP_BUILD_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share", "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["llcpp"]
        self.cpp_info.set_property("cmake_file_name", "ll-cpp")
        self.cpp_info.set_property("cmake_target_name", "llcpp::llcpp")
