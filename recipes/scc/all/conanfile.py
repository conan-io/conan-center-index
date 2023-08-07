import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, export_conandata_patches, apply_conandata_patches
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class SystemcComponentsConan(ConanFile):
    name = "scc"
    description = "A light weight productivity library for SystemC and TLM 2.0"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://minres.github.io/SystemC-Components"
    topics = ("systemc", "modeling", "tlm", "scc")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_phase_callbacks": [True, False],
        "enable_phase_callbacks_tracing": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_phase_callbacks": False,
        "enable_phase_callbacks_tracing": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fmt/10.1.1")
        self.requires("zlib/1.2.13")
        self.requires("boost/1.83.0")
        self.requires("gsl-lite/0.41.0")
        self.requires("spdlog/1.12.0")
        self.requires("systemc/2.3.4")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if is_apple_os(self):
            raise ConanInvalidConfiguration(f"{self.name} is not suppported on {self.settings.os}.")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration("GCC < version 7 is not supported")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SC_WITH_PHASE_CALLBACKS"] = self.options.enable_phase_callbacks
        tc.variables["SC_WITH_PHASE_CALLBACK_TRACING"] = self.options.enable_phase_callbacks_tracing
        tc.variables["BUILD_SCC_DOCUMENTATION"] = False
        tc.variables["SCC_LIB_ONLY"] = True
        tc.variables["ENABLE_CONAN"] = False
        if self.settings.os == "Windows":
            tc.variables["SCC_LIMIT_TRACE_TYPE_LIST"] = True
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["busses"].libs = ["busses"]
        self.cpp_info.components["scc-sysc"].libs = ["scc-sysc"]
        self.cpp_info.components["scc-util"].libs = ["scc-util"]
        self.cpp_info.components["scv-tr"].libs = ["scv-tr"]
        self.cpp_info.components["tlm-interfaces"].libs = ["tlm-interfaces"]
