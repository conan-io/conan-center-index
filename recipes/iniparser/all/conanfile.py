from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class iniparserConan(ConanFile):
    name = "iniparser"
    description = "iniParser is a simple C library offering ini file parsing services."
    license = "MIT"
    url = "https://gitlab.com/iniparser/iniparser"
    homepage = "https://iniparser.gitlab.io/iniparser/"
    topics = ("ini", "parser", "configuration", "file")

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
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.cache_variables["BUILD_TESTING"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["iniparser"]

        self.cpp_info.set_property("cmake_file_name", "iniparser")
        self.cpp_info.set_property("cmake_target_name", "iniparser::iniparser")
        self.cpp_info.set_property("pkg_config_name", "iniparser")
        self.cpp_info.includedirs = ["include", os.path.join("include", "iniparser")]
