import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.1"


class GslLiteConan(ConanFile):
    name = "gsl-lite"
    description = "ISO C++ Core Guidelines Library implementation for C++98, C++11 up"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gsl-lite/gsl-lite"
    topics = ("GSL", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        copy(self, "LICENSE",  src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "gsl-lite")
        self.cpp_info.set_property("cmake_target_name", "gsl-lite::gsl-lite")
        self.cpp_info.set_property("cmake_target_aliases", ["gsl::gsl-lite"])

        self.cpp_info.set_property("cmake_config_version_compat", "SameMajorVersion")



        # The package also defines the versioned targets `gsl::gsl-lite-v0`, `gsl::gsl-lite-v1`,
        # `gsl-lite::gsl-lite-v0` and `gsl-lite::gsl-lite-v1`. Versioned targets `*-v<X>` for which
        # <X> differs from the major version of the package add a compile definition
        # `gsl_CONFIG_DEFAULTS_VERSION=<X>`. These targets are not exposed here.
