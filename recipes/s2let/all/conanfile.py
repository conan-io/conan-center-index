import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class S2let(ConanFile):
    name = "s2let"
    description = "Fast wavelets on the sphere"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/astro-informatics/s2let"
    topics = ("physics", "astrophysics", "radio interferometry")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_cfitsio": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_cfitsio": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("astro-informatics-so3/1.3.6", transitive_headers=True, transitive_libs=True)
        if self.options.with_cfitsio:
            self.requires("cfitsio/4.3.1")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("S2LET requires C99 support for complex numbers.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["cfitsio"] = self.options.with_cfitsio
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.cmake", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["s2let"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
