from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rmdir
from conan.tools.cmake import CMake, cmake_layout
import os

required_conan_version = ">=2.1"

class DylibConan(ConanFile):
    name = "dylib"
    homepage = "https://github.com/martin-olivier/dylib"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++ cross-platform wrapper around dynamic loading of shared libraries (dll, so, dylib)"
    license = "MIT"
    topics = ("shared-library", "cross-platform", "dynamic-loading")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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
        self.cpp_info.set_property("cmake_file_name", "dylib")
        self.cpp_info.set_property("cmake_target_name", "dylib::dylib")
        self.cpp_info.set_property("pkg_config_name", "dylib")

        self.cpp_info.libs = ["dylib"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl"])
