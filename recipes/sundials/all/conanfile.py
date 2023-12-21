from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, mkdir
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
        if self.settings.os == "Windows" and self.options.shared:
            mkdir(self, os.path.join(self.package_folder, "bin"))
            for dll_path in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
                shutil.move(dll_path, os.path.join(self.package_folder, "bin", os.path.basename(dll_path)))

    def package_info(self):
        self.cpp_info.components["sundials_nvecmanyvector"].libs = ["sundials_nvecmanyvector"]
        self.cpp_info.components["sundials_nvecserial"].libs = ["sundials_nvecserial"]
        self.cpp_info.components["sundials_sunlinsolband"].libs = ["sundials_sunlinsolband"]
        self.cpp_info.components["sundials_sunlinsolband"].requires = ["sundials_sunmatrixband"]
        self.cpp_info.components["sundials_sunlinsoldense"].libs = ["sundials_sunlinsoldense"]
        self.cpp_info.components["sundials_sunlinsoldense"].requires = ["sundials_sunmatrixdense"]
        self.cpp_info.components["sundials_sunlinsolpcg"].libs = ["sundials_sunlinsolpcg"]
        self.cpp_info.components["sundials_sunlinsolspbcgs"].libs = ["sundials_sunlinsolspbcgs"]
        self.cpp_info.components["sundials_sunlinsolspfgmr"].libs = ["sundials_sunlinsolspfgmr"]
        self.cpp_info.components["sundials_sunlinsolspgmr"].libs = ["sundials_sunlinsolspgmr"]
        self.cpp_info.components["sundials_sunlinsolsptfqmr"].libs = ["sundials_sunlinsolsptfqmr"]
        self.cpp_info.components["sundials_sunmatrixband"].libs = ["sundials_sunmatrixband"]
        self.cpp_info.components["sundials_sunmatrixdense"].libs = ["sundials_sunmatrixdense"]
        self.cpp_info.components["sundials_sunmatrixsparse"].libs = ["sundials_sunmatrixsparse"]
        self.cpp_info.components["sundials_sunnonlinsolfixedpoint"].libs = ["sundials_sunnonlinsolfixedpoint"]
        self.cpp_info.components["sundials_sunnonlinsolnewton"].libs = ["sundials_sunnonlinsolnewton"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["sundials_nvecmanyvector"].system_libs = ["m"]
            self.cpp_info.components["sundials_nvecserial"].system_libs = ["m"]
            self.cpp_info.components["sundials_sunlinsolpcg"].system_libs = ["m"]
            self.cpp_info.components["sundials_sunlinsolspbcgs"].system_libs = ["m"]
            self.cpp_info.components["sundials_sunlinsolspfgmr"].system_libs = ["m"]
            self.cpp_info.components["sundials_sunlinsolspgmr"].system_libs = ["m"]
            self.cpp_info.components["sundials_sunlinsolsptfqmr"].system_libs = ["m"]
            self.cpp_info.components["sundials_sunmatrixband"].system_libs = ["m"]
            self.cpp_info.components["sundials_sunmatrixdense"].system_libs = ["m"]
            self.cpp_info.components["sundials_sunmatrixsparse"].system_libs = ["m"]
            self.cpp_info.components["sundials_sunnonlinsolfixedpoint"].system_libs = ["m"]
            self.cpp_info.components["sundials_sunnonlinsolnewton"].system_libs = ["m"]
        if self.options.build_arkode:
            self.cpp_info.components["sundials_arkode"].libs = ["sundials_arkode"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["sundials_arkode"].system_libs = ["m"]
        if self.options.build_cvode:
            self.cpp_info.components["sundials_cvode"].libs = ["sundials_cvode"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["sundials_cvode"].system_libs = ["m"]
        if self.options.build_cvodes:
            self.cpp_info.components["sundials_cvodes"].libs = ["sundials_cvodes"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["sundials_cvodes"].system_libs = ["m"]
        if self.options.build_ida:
            self.cpp_info.components["sundials_ida"].libs = ["sundials_ida"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["sundials_ida"].system_libs = ["m"]
        if self.options.build_idas:
            self.cpp_info.components["sundials_idas"].libs = ["sundials_idas"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["sundials_idas"].system_libs = ["m"]
        if self.options.build_kinsol:
            self.cpp_info.components["sundials_kinsol"].libs = ["sundials_kinsol"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["sundials_kinsol"].system_libs = ["m"]
