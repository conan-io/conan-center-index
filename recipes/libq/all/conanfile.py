import os

from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.files import collect_libs
from conan.tools.apple import fix_apple_shared_install_name

required_conan_version = ">=2.0.0"

class libqConan(ConanFile):
    name = "libq"
    description = "A platform-independent promise library for C++, implementing asynchronous continuations."
    license = "Apache license 2.0"
    url = "https://github.com/grantila/q"
    homepage = "https://github.com/grantila/q"
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"
    options = {
        "shared"            : [True, False],
        "qtest"            : [True, False],
        "cpp17"            : [True, False],
        "cpp20"            : [True, False]
    }
    default_options = {
        "shared"            : False,
        "qtest"            : True,
        "cpp17"            : False,
        "cpp20"            : False
    }

    def optionBool(self, b):
        if b:
            return "ON"
        else:
            return "OFF"

    def parseOptionsToCMake(self):
        cmakeOpts = {
            "q_BUILD_TESTS" : "OFF"
        }

        cmakeOpts["BUILD_SHARED_LIBS"] = self.optionBool(self.options.shared)
        cmakeOpts["q_BUILD_QTEST"] = self.optionBool(self.options.qtest)
        if self.options.cpp20:
            cmakeOpts["CMAKE_CXX_STANDARD"] = 20
            cmakeOpts["CMAKE_CXX_STANDARD_REQUIRED"] = 20
        if self.options.cpp17:
            cmakeOpts["CMAKE_CXX_STANDARD"] = 17
            cmakeOpts["CMAKE_CXX_STANDARD_REQUIRED"] = 17

        return cmakeOpts

    def build(self):
        cmake = CMake(self)
        cmake.configure(variables=self.parseOptionsToCMake())
        cmake.build()
        cmake.install()
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
