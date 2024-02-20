import os

from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.files import collect_libs
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import get
from conan.tools.build import check_min_cppstd

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
        "qtest"            : [True, False]
    }
    default_options = {
        "shared"            : False,
        "qtest"            : False
    }

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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

        return cmakeOpts

    def build(self):
        cmake = CMake(self)
        cmake.configure(variables=self.parseOptionsToCMake())
        cmake.build()
        cmake.install()
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
