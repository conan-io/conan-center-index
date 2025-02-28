from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.cmake.cmakedeps.cmakedeps import CMakeDeps
from conan.tools.files import copy, get, rmdir
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.1"


class SpectraConan(ConanFile):
    name = "spectra"
    description = "A header-only C++ library for large scale eigenvalue problems."
    license = "MPL-2.0"
    topics = ("eigenvalue", "header-only")
    homepage = "https://spectralib.org"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if Version(self.version) >= "1.0.0":
            check_min_cppstd(self, 11)

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
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "spectra")
        self.cpp_info.set_property("cmake_target_name", "Spectra::Spectra")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
