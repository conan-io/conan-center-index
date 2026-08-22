from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rmdir
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain, CMakeDeps
import os

required_conan_version = ">=2"


class InjaConan(ConanFile):
    name = "inja"
    license = "MIT"
    homepage = "https://github.com/pantor/inja"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Inja is a template engine for modern C++, loosely inspired by jinja for python"
    topics = ("jinja2", "string templates", "templates engine")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("nlohmann_json/[^3.8]")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["INJA_BUILD_TESTS"] = False
        tc.cache_variables["INJA_EXPORT"] = False
        tc.cache_variables["INJA_USE_EMBEDDED_JSON"] = False
        tc.cache_variables["INJA_INSTALL"] = True
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "inja")
        self.cpp_info.set_property("cmake_target_name", "pantor::inja")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
