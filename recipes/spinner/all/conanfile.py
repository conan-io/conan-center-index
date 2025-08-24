from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import copy, get, rmdir, rm
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.1"

class SpinnerConan(ConanFile):
    name = "spinner"
    version = "0.1.0"
    description = "A C++ library providing a terminal spinner for CLI apps."
    license = "MIT"
    topics = ("cli", "spinner", "utility")
    homepage = "https://github.com/vishal-ahirwar/spinner"
    url = "https://github.com/vishal-ahirwar/spinner"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps"
    no_copy_source = False

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("fmt/11.2.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        rm(self, "*-config*", os.path.join(self.package_folder, "bin"), ignore_missing=True)
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "bin", "cmake"), ignore_errors=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "spinner")
        self.cpp_info.set_property("cmake_target_name", "spinner::spinner")
        self.cpp_info.libs = ["spinner"] 