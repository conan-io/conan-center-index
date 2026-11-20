from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os

required_conan_version = ">=1.53.0"


class TesultsCppConan(ConanFile):
    name = "tesults-cpp"
    description = "C++ library for uploading test results to Tesults"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tesults/cpp"
    topics = ("tesults", "testing", "test-results", "reporting")
    package_type = "static-library"
    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libcurl/[>=7.64.0 <9]")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("nlohmann_json/[>=3.9.0 <4]")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["tesults"]
        self.cpp_info.set_property("cmake_file_name", "tesults")
        self.cpp_info.set_property("cmake_target_name", "tesults::tesults")
