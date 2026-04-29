from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=2.1"

class ConsteigConan(ConanFile):
    name = "consteig"
    description = (
        "Header-only C++17 constexpr library for compile-time "
        "eigenvalue and eigenvector computation"
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/MitchellThompkins/consteig"
    topics = ("constexpr", "eigenvalues", "eigenvectors", "linear-algebra",
              "header-only", "freestanding", "compile-time")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    implements = ["auto_header_only"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        check_min_cppstd(self, 17)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CONSTEIG_VERSION"] = self.version
        tc.variables["CONSTEIG_BUILD_TESTS"] = False
        tc.variables["CONSTEIG_BUILD_EXAMPLES"] = False
        tc.variables["CONSTEIG_BUILD_PROFILING"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
