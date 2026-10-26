import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir


required_conan_version = ">=2.0.9"


class PiDWGConan(ConanFile):
    name = "pidwg"
    description = "Cross-platform C++ library for reading DWG files into a version-independent CAD object model"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.com/vanavara/piDWG"
    topics = ("dwg", "cad", "reader", "geometry")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "17")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.cache_variables["BUILD_SHARED_LIBS"] = False
        toolchain.cache_variables["BUILD_TESTING"] = False
        toolchain.cache_variables["PIDWG_BUILD_TOOLS"] = False
        toolchain.cache_variables["PIDWG_BUILD_EXAMPLES"] = False
        if self.options.get_safe("fPIC") is not None:
            toolchain.cache_variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "piDWG")
        self.cpp_info.set_property("cmake_target_name", "piDWG::piDWG")
        self.cpp_info.set_property("pkg_config_name", "pidwg")
        self.cpp_info.libs = ["piDWG"]
