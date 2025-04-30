from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class CppUTestConan(ConanFile):
    name = "cpputest"
    description = (
        "CppUTest is a C /C++ based unit xUnit test framework for unit testing "
        "and for test-driving your code. It is written in C++ but is used in C "
        "and C++ projects and frequently used in embedded systems but it works "
        "for any C/C++ project."
    )
    license = "BSD-3-Clause"
    topics = ("testing", "unit-testing")
    homepage = "https://cpputest.github.io"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_extensions": [True, False],
        "with_leak_detection": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_extensions": True,
        "with_leak_detection": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["STD_C"] = True
        tc.variables["STD_CPP"] = True
        tc.variables["C++11"] = True
        tc.variables["MEMORY_LEAK_DETECTION"] = self.options.with_leak_detection
        tc.variables["EXTENSIONS"] = self.options.with_extensions
        tc.variables["LONGLONG"] = True
        tc.variables["COVERAGE"] = False
        tc.variables["TESTS"] = False
        if Version(self.version) <= "4.0": # Master branch already support CMake 4 (not yet released)
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "CppUTest"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CppUTest")
        self.cpp_info.set_property("pkg_config_name", "cpputest")

        self.cpp_info.components["CppUTest"].set_property("cmake_target_name", "CppUTest")
        self.cpp_info.components["CppUTest"].libs = ["CppUTest"]
        if self.settings.os == "Windows":
            self.cpp_info.components["CppUTest"].system_libs.append("winmm")
        elif self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["CppUTest"].system_libs.append("pthread")

        if self.options.with_extensions:
            self.cpp_info.components["CppUTestExt"].set_property("cmake_target_name", "CppUTestExt")
            self.cpp_info.components["CppUTestExt"].libs = ["CppUTestExt"]
            self.cpp_info.components["CppUTestExt"].requires = ["CppUTest"]
