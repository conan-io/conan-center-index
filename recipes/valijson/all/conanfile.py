from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import get, copy
import os

required_conan_version = ">=2.0"


class ValijsonConan(ConanFile):
    name = "valijson"
    description = "Header-only C++ library for JSON Schema validation, with support for many popular parsers"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tristanpenman/valijson"
    topics = ("json", "validator", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("poco/1.13.3")
        self.requires("qt/[>=5.15 <6]")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

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

    def package_id(self):
        self.info.clear()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "valijson")
        self.cpp_info.set_property("cmake_target_name", "ValiJSON::valijson")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
