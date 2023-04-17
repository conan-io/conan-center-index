from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=1.52.0"

class CLI11Conan(ConanFile):
    name = "cli11"
    homepage = "https://github.com/CLIUtils/CLI11"
    description = "A command line parser for C++11 and beyond."
    topics = "cli-parser", "cpp11", "no-dependencies", "cli", "header-only"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _min_cppstd(self):
        return "11"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CLI11_BUILD_EXAMPLES"] = False
        tc.variables["CLI11_BUILD_TESTS"] = False
        tc.variables["CLI11_BUILD_DOCS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # since 2.1.1
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CLI11")
        self.cpp_info.set_property("cmake_target_name", "CLI11::CLI11")
        self.cpp_info.set_property("pkg_config_name", "CLI11")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "CLI11"
        self.cpp_info.names["cmake_find_package_multi"] = "CLI11"
        self.cpp_info.names["pkg_config"] = "CLI11"
