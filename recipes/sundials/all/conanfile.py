from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, mkdir, rmdir
from conan.tools.apple import fix_apple_shared_install_name
import glob
import os
import shutil

required_conan_version = ">=1.53.0"


class SundialsConan(ConanFile):
    name = "sundials"
    license = "BSD-3-Clause"
    description = ("SUNDIALS is a family of software packages implemented"
                   " with the goal of providing robust time integrators "
                   "and nonlinear solvers that can easily be incorporated"
                   "into existing simulation codes.")
    topics = ("integrators", "ode", "non-linear solvers")
    homepage = "https://github.com/LLNL/sundials"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_arkode": [True, False],
        "build_cvode": [True, False],
        "build_cvodes": [True, False],
        "build_ida": [True, False],
        "build_idas": [True, False],
        "build_kinsol": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_arkode": True,
        "build_cvode": True,
        "build_cvodes": True,
        "build_ida": True,
        "build_idas": True,
        "build_kinsol": True,
    }

    short_paths = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.18]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["BUILD_ARKODE"] = self.options.build_arkode
        tc.variables["BUILD_CVODE"] = self.options.build_cvode
        tc.variables["BUILD_CVODES"] = self.options.build_cvodes
        tc.variables["BUILD_IDA"] = self.options.build_ida
        tc.variables["BUILD_IDAS"] = self.options.build_idas
        tc.variables["BUILD_KINSOL"] = self.options.build_kinsol
        tc.variables["EXAMPLES_ENABLE_C"] = False
        tc.variables["EXAMPLES_INSTALL"] = False
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
        if self.settings.os == "Windows" and self.options.shared:
            mkdir(self, os.path.join(self.package_folder, "bin"))
            for dll_path in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
                shutil.move(dll_path, os.path.join(self.package_folder, "bin", os.path.basename(dll_path)))
        fix_apple_shared_install_name(self)

    def package_info(self):

        def _add_library(name):
            # SundialsAddLibrary.cmake#377, where the first branch is always taken.
            library_suffix = "_static" if not self.options.shared and self.settings.compiler == "msvc" else ""
            self.cpp_info.components[name].libs = ["sundials_" + name + library_suffix]
            target_suffix = "_shared" if self.options.shared else "_static"
            self.cpp_info.components[name].set_property("cmake_target_name", f"SUNDIALS::{name}{target_suffix}")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components[name].system_libs.append("m")
            return self.cpp_info.components[name]

        _add_library("core")
        _add_library("nvecserial").requires = ["core"]
        _add_library("nvecmanyvector").requires = ["core"]
        _add_library("sunmatrixdense").requires = ["core"]
        _add_library("sunmatrixband").requires = ["core"]
        _add_library("sunmatrixsparse").requires = ["core"]
        _add_library("sundomeigestpower").requires = ["core"]
        _add_library("sunlinsoldense").requires = ["core", "sunmatrixdense"]
        _add_library("sunlinsolband").requires = ["core", "sunmatrixband"]
        _add_library("sunlinsolpcg").requires = ["core"]
        _add_library("sunlinsolspbcgs").requires = ["core"]
        _add_library("sunlinsolspfgmr").requires = ["core"]
        _add_library("sunlinsolspgmr").requires = ["core"]
        _add_library("sunlinsolsptfqmr").requires = ["core"]
        _add_library("sunnonlinsolfixedpoint").requires = ["core"]
        _add_library("sunnonlinsolnewton").requires = ["core"]

        if self.options.build_arkode:
            _add_library("arkode").requires = ["core"]
        if self.options.build_cvode:
            _add_library("cvode").requires = ["core"]
        if self.options.build_cvodes:
            _add_library("cvodes").requires = ["core"]
        if self.options.build_ida:
            _add_library("ida").requires = ["core"]
        if self.options.build_idas:
            _add_library("idas").requires = ["core"]
        if self.options.build_kinsol:
            _add_library("kinsol").requires = ["core"]
