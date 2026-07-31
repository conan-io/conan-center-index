import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, rmdir, get


class UnitsConan(ConanFile):
    name = "llnl-units"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://units.readthedocs.io"
    description = (
        "A run-time C++ library for working with units "
        "of measurement and conversions between them "
        "and with string representations of units "
        "and measurements"
    )
    topics = (
        "units",
        "dimensions",
        "quantities",
        "physical-units",
        "dimensional-analysis",
        "run-time",
    )
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["UNITS_ENABLE_TESTS"] = False
        tc.generate()

    def validate(self):
        check_min_cppstd(self, 14)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["units"]
        self.cpp_info.set_property("cmake_file_name", "units")
        self.cpp_info.set_property("cmake_target_name", "units::units")
