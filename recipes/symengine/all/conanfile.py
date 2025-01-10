from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import (
    collect_libs,
    copy,
    get,
    rm,
    rmdir,
    replace_in_file,
)
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version

import os
required_conan_version = ">=2.1"


class SymengineConan(ConanFile):
    name = "symengine"
    description = "A fast symbolic manipulation library, written in C++"
    license = "MIT"
    topics = ("symbolic", "algebra")
    homepage = "https://symengine.org/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
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

    def layout(self):
        basic_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
    
    def validate(self):
        min_cppstd = "11"
        check_min_cppstd(self, min_cppstd)

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration(f"{self.ref} requires GCC >= 7")

    @property
    def _needs_fast_float(self):
        return Version(self.version) >= "0.13.0"

    def requirements(self):
        if self.options.integer_class == "boostmp":
            # symengine/mp_class.h:12
            self.requires("boost/1.86.0", transitive_headers=True)
        else:
            self.requires("gmp/6.3.0", transitive_headers=True, transitive_libs=True)
        if self._needs_fast_float:
            self.requires("fast_float/6.1.5")

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self.source_folder,
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_BENCHMARKS"] = False
        tc.variables["INTEGER_CLASS"] = self.options.integer_class
        tc.variables["MSVC_USE_MT"] = is_msvc_static_runtime(self)
        if self._needs_fast_float:
            tc.variables["WITH_SYSTEM_FASTFLOAT"] = True

        tc.generate()
        deps = CMakeDeps(self)
        if self.options.integer_class == "gmp":
            deps.set_property("gmp", "cmake_file_name", "GMP")
            # If we ever add support for gmpxx, we should set this property
            # if self.dependencies["gmp"].options.enable_cxx:
            #     deps.set_property("gmp::gmpxx", "cmake_target_name", "gmpxx")
        if self._needs_fast_float:
            deps.set_property("fast_float", "cmake_file_name", "FASTFLOAT")
        deps.generate()

    def _patch_sources(self):
        # Disable hardcoded C++11
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'set(CMAKE_CXX_FLAGS "${CXX11_OPTIONS} ${CMAKE_CXX_FLAGS}")',
                        '')
        # Let Conan choose fPIC
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${common}")',
                        '')
        # cmake_target_name not working?
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(LIBS ${LIBS} ${GMP_TARGETS})",
                        "set(LIBS ${LIBS} gmp::gmp)")

    def build(self):
        self._patch_sources()
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

        self.cpp_info.set_property("cmake_target_name", "symengine")
