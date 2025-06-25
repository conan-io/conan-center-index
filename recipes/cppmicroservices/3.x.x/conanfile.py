from conan import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import get, replace_in_file

import os

class CppMicroServicesConan(ConanFile):
    name = "cppmicroservices"
    package_type = "library"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_gtest": [True, False],
        "with_doxygen": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_gtest" : False,
        "with_doxygen" : False
    }

    def source(self):
        # we recover the saved url and commit from conandata.yml and use them to get sources
        git = Git(self)
        git.clone(url=self.conan_data["sources"][self.version]["url"], args=["--recurse-submodules"], hide_url=False)
        git.checkout(commit=self.conan_data["sources"][self.version]["sha1"])
#        replace_in_file(self, os.path.join(self.target, "third_party", "boost", "nowide", "include", "nowide", "detail", "convert.hpp"),
#                        "::template ", "::")

    # def config_options(self):
    #     if self.settings.os == "Windows":
    #         self.options.rm_safe("fPIC")

    # def configure(self):
    #     os.environ["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
    #     if self.options.shared:
    #         self.options.rm_safe("fPIC")

    # def generate(self):
    #     deps = CMakeDeps(self)
    #     deps.generate()
    #     tc = CMakeToolchain(self)
    #     tc.generate()

    # def build(self):
    #     cmake = CMake(self)
    #     cmake.configure(variables={"US_BUILD_TESTING":"On"},
    #                     build_script_folder=self.target)
    #     cmake.build()
    #     cmake.test()

    # def package(self):
    #     cmake = CMake(self)
    #     cmake.install()

    # def package_info(self):
    #     self.cpp_info.libs = ["cppmicroservices"]
