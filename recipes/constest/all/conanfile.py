from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, get


class ConsTestConan(ConanFile):
    name = "constest"
    version = "1.0.0"
    license = "MIT"
    author = "Clément Metz"
    url = "https://github.com/Teskann/constest"
    description = "C++20 testing framework extension for compile-time expressions. Compatible with GTest, Catch2, Doctest and Boost.Test"
    topics = ("testing", "compile-time", "constexpr", "header-only")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "CMakeLists.txt", "constest/*"
    package_type = "header-library"

    def layout(self):
        cmake_layout(self)

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CONAN_EXPORTED"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE.md", src=self.source_folder, dst=self.package_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = ["constest"]
        self.cpp_info.set_property("cmake_file_name", "constest")
        self.cpp_info.set_property("cmake_target_name", "constest::constest")
