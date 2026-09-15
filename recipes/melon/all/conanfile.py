import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rmdir
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMake

required_conan_version = ">=2.1"


class MelonConan(ConanFile):
    name = "melon"
    description = "Modern and Efficient Library for Optimization in Networks."
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/fhamonic/melon"
    topics = ("graph", "header-only", "cpp23", "algorithms")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 23)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["MELON_BUILD_TESTS"] = False
        tc.generate()

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
