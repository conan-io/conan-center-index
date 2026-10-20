from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_max_cppstd, check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class ZmijConan(ConanFile):
    name = "zmij"
    description = "A fast floating-point-to-string conversion library for C and C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/vitaut/zmij"
    topics = ("dtoa", "float", "double", "floating-point", "ieee754", "performance")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
            self.options.rm_safe("shared")
            self.package_type = "static-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 14)

    def validate_build(self):
        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "21":
            raise ConanInvalidConfiguration("Needs apple-clang >=21")
        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "21":
            # https://github.com/vitaut/zmij/issues/169
            check_max_cppstd(self, 14)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ZMIJ_TEST"] = False
        tc.cache_variables["ZMIJ_EXAMPLE"] = False
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
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "zmij")
        self.cpp_info.set_property("cmake_target_name", "zmij::zmij")
        self.cpp_info.libs = ["zmij"]
