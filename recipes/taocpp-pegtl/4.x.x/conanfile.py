from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
import os

required_conan_version = ">=2.4"


class TaoCPPPEGTLConan(ConanFile):
    name = "taocpp-pegtl"
    description = "Parsing Expression Grammar Template Library"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/pegtl"
    topics = ("peg", "header-only",  "parsing", "grammar")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def package(self):
        copy(self, "LICENSE_1_0.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "pegtl")
        self.cpp_info.set_property("cmake_target_name", "taocpp::pegtl")
        self.cpp_info.set_property("pkg_config_name", "pegtl")
