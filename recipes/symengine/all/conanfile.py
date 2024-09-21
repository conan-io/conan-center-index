from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import (
    apply_conandata_patches,
    collect_libs,
    copy,
    get,
    rm,
    rmdir,
)
import os

required_conan_version = ">=1.54.0"


class SymengineConan(ConanFile):
    name = "symengine"
    description = "A fast symbolic manipulation library, written in C++"
    license = "MIT"
    topics = ("symbolic", "algebra")
    homepage = "https://symengine.org/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "integer_class": ["boostmp", "gmp"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "integer_class": "gmp",
    }
    short_paths = True

    def requirements(self):
        if self.options.integer_class == "boostmp":
            self.requires("boost/1.83.0")
        else:
            self.requires("gmp/6.3.0", transitive_headers=True, transitive_libs=True)

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self.source_folder,
        )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_BENCHMARKS"] = False
        tc.variables["INTEGER_CLASS"] = self.options.integer_class
        tc.variables["MSVC_USE_MT"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        # [CMAKE-MODULES-CONFIG-FILES (KB-H016)]
        rm(self, "*.cmake", self.package_folder, recursive=True)
        # [DEFAULT PACKAGE LAYOUT (KB-H013)]
        rmdir(self, os.path.join(self.package_folder, "CMake"))

    def package_info(self):
        self.cpp_info.libs = ["symengine"]
        if any("teuchos" in v for v in collect_libs(self)):
            self.cpp_info.libs.append("teuchos")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        self.cpp_info.names["cmake_find_package"] = "symengine"
        # FIXME: symengine exports a non-namespaced `symengine` target.
        self.cpp_info.names["cmake_find_package_multi"] = "symengine"
