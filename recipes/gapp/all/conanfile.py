from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
import os

required_conan_version = ">=2.0.9"

class GappConan(ConanFile):
    name = "gapp"
    description = "A genetic algorithms library in C++ for single- and multi-objective optimization."
    topics = ("genetic-algorithm", "optimization", "multi-objective-optimization", "constrained-optimization")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KRM7/gapp"
    license = "MIT"
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"

    options = { "shared": [True, False], "fPIC": [True, False] }
    default_options = { "shared": False, "fPIC": True }

    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 20)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["GAPP_BUILD_TESTS"] = False
        tc.cache_variables["GAPP_USE_WERROR"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libdirs = [os.path.join("lib", str(self.settings.build_type))]
        self.cpp_info.bindirs = [os.path.join("lib", str(self.settings.build_type))]
        prefix = "lib" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.libs = [f"{prefix}gapp"]
