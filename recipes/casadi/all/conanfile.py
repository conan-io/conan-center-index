import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "casadi"
    description = "CasADi is a symbolic framework for automatic differentation and numeric optimization"
    license = "LGPL-3.0-or-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://casadi.org"
    topics = ("optimization", "nonlinear", "numerical-calculations", "scientific-computing", "derivatives",
              "code-generation", "parameter-estimation", "optimal-control", "symbolic-manipulation",
              "algorithmic-differentation", "nonlinear-programming")

    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_deprecated": [True, False],
        "with_alpaqa": [True, False],
        "with_blasfeo": [True, False],
        "with_bonmin": [True, False],
        "with_cbc": [True, False],
        "with_clp": [True, False],
        "with_csparse": [True, False],
        "with_dsdp": [True, False],
        "with_fatrop": [True, False],
        "with_highs": [True, False],
        "with_hpipm": [True, False],
        "with_hsl": [True, False],
        "with_ipopt": [True, False],
        "with_lapack": [True, False],
        "with_mumps": [True, False],
        "with_opencl": [True, False],
        "with_openmp": [True, False],
        "with_osqp": [True, False],
        "with_proxqp": [True, False],
        "with_pthread": [True, False],
        "with_qpoases": [True, False],
        "with_sleqp": [True, False],
        "with_spral": [True, False],
        "with_sundials": [True, False],
        "with_superscs": [True, False],
        "with_tinyxml": [True, False],
    }
    default_options = {
        "enable_deprecated": True,
        "with_alpaqa": False,
        "with_blasfeo": False,
        "with_bonmin": False,
        "with_cbc": True,
        "with_clp": True,
        "with_csparse": True,
        "with_dsdp": False,
        "with_fatrop": False,
        "with_highs": False,
        "with_hpipm": False,
        "with_hsl": False,
        "with_ipopt": True,
        "with_lapack": True,
        "with_mumps": True,
        "with_opencl": False,
        "with_openmp": True,
        "with_osqp": True,
        "with_proxqp": False,
        "with_pthread": False,
        "with_qpoases": True,
        "with_sleqp": False,
        "with_spral": False,
        "with_sundials": True,
        "with_superscs": False,
        "with_tinyxml": True,
    }
    options_description = {
        "enable_deprecated": "Compile with syntax that is scheduled to be deprecated",
        "with_alpaqa": "Compile the Alpaqa interface",
        "with_blasfeo": "Compile the interface to BLASFEO (vendored by CasADi)",
        "with_bonmin": "Compile the interface to BONMIN (vendored by CasADi)",
        "with_cbc": "Compile the CBC interface",
        "with_clp": "Compile the CLP interface",
        "with_csparse": "Compile the interface to CSparse (vendored by CasADi)",
        "with_dsdp": "Compile the interface to DSDP (vendored by CasADi)",
        "with_fatrop": "Compile the interface to FATROP (vendored by CasADi)",
        "with_highs": "Compile the HiGHS interface (vendored by CasADi)",
        "with_hpipm": "Compile the interface to HPIPM (vendored by CasADi)",
        "with_hsl": "Enable HSL interface (vendored by CasADi)",
        "with_ipopt": "Compile the interface to IPOPT",
        "with_lapack": "Compile the interface to LAPACK",
        "with_mumps": "Enable MUMPS interface",
        "with_opencl": "Compile with OpenCL support (experimental)",
        "with_openmp": "Compile with parallelization support using OpenMP",
        "with_osqp": "Compile the interface to OSQP",
        "with_proxqp": "Compile the interface to PROXQP (vendored by CasADi)",
        "with_pthread": "Compile with parallelization support using POSIX Threads",
        "with_qpoases": "Compile the interface to qpOASES (vendored by CasADi)",
        "with_sleqp": "Compile the interface to SLEQP (vendored by CasADi)",
        "with_spral": "Enable SPRAL interface (vendored by CasADi)",
        "with_sundials": "Compile the interface to Sundials (vendored by CasADi)",
        "with_superscs": "Compile the interface to SuperSCS (vendored by CasADi)",
        "with_tinyxml": "Compile the interface to TinyXML",
    }

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_alpaqa or self.options.with_proxqp:
            self.requires("eigen/3.4.0")
        if self.options.with_openmp and self.settings.compiler in ["clang", "apple-clang"]:
            self.requires("llvm-openmp/17.0.4")
        if self.options.with_pthread and self.settings.os == "Windows":
            self.requires("pthreads4w/3.0.0")
        if self.options.with_opencl:
            self.requires("opencl-headers/2023.04.17")
        if self.options.with_osqp:
            self.requires("osqp/0.6.2")
        if self.options.with_tinyxml:
            self.requires("tinyxml/2.6.2")
        if self.options.with_lapack:
            self.requires("openblas/0.3.25")
        if self.options.with_ipopt:
            self.requires("coin-ipopt/3.14.13")
        if self.options.with_cbc:
            self.requires("coin-cbc/2.10.5")
        if self.options.with_clp:
            self.requires("coin-clp/1.17.7")
        if self.options.with_mumps:
            self.requires("coin-mumps/3.0.5")
        if self.options.with_bonmin:
            self.requires("coin-cgl/0.60.7")
            self.requires("coin-osi/0.108.7")
            self.requires("coin-utils/2.11.9")
        if self.options.with_spral:
            self.requires("metis/5.2.1")

        # FIXME: SUNDIALS v5+ available from CCI is not compatible
        # CasADi vendors v2.6.1
        # if self.options.with_sundials:
        #     self.requires("sundials/5.4.0")

        # qpOASES is always built by the project
        # TODO: maybe unvendor it
        # if self.options.with_qpoases:
        #     self.requires("qpoases/3.2.1")

        # FIXME: unvendor simde
        # if self.options.with_proxqp:
        #     self.requires("simde/0.7.6")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=False)

    def generate(self):
        tc = CMakeToolchain(self)
        # Static builds are disabled due to requiring WITH_DL=False,
        # which fails with a compilation error as of v3.6.4.
        tc.variables["ENABLE_SHARED"] = True
        tc.variables["ENABLE_STATIC"] = False
        tc.variables["WITH_DL"] = True
        tc.variables["WITH_EXAMPLES"] = False
        tc.variables["WITH_DEPRECATED_FEATURES"] = self.options.enable_deprecated
        tc.variables["WITH_BUILD_REQUIRED"] = False

        tc.variables["WITH_ALPAQA"] = self.options.with_alpaqa
        tc.variables["WITH_AMPL"] = False
        tc.variables["WITH_BLASFEO"] = self.options.with_blasfeo
        tc.variables["WITH_BLOCKSQP"] = False
        tc.variables["WITH_BONMIN"] = self.options.with_bonmin
        tc.variables["WITH_CBC"] = self.options.with_cbc
        tc.variables["WITH_CLANG"] = False
        tc.variables["WITH_CLP"] = self.options.with_clp
        tc.variables["WITH_COINCGL"] = self.options.with_bonmin
        tc.variables["WITH_COINOSI"] = self.options.with_bonmin
        tc.variables["WITH_COINUTILS"] = self.options.with_bonmin
        tc.variables["WITH_CPLEX"] = False
        tc.variables["WITH_CSPARSE"] = self.options.with_csparse
        tc.variables["WITH_DSDP"] = self.options.with_dsdp
        tc.variables["WITH_FATROP"] = self.options.with_fatrop
        tc.variables["WITH_GUROBI"] = False
        tc.variables["WITH_HIGHS"] = self.options.with_highs
        tc.variables["WITH_HPIPM"] = self.options.with_hpipm
        tc.variables["WITH_HSL"] = self.options.with_hsl
        tc.variables["WITH_IPOPT"] = self.options.with_ipopt
        tc.variables["WITH_KNITRO"] = False
        tc.variables["WITH_LAPACK"] = self.options.with_lapack
        tc.variables["WITH_MUMPS"] = self.options.with_mumps
        tc.variables["WITH_OOQP"] = False
        tc.variables["WITH_OPENCL"] = self.options.with_opencl
        tc.variables["WITH_OPENMP"] = self.options.with_openmp
        tc.variables["WITH_OSQP"] = self.options.with_osqp
        tc.variables["WITH_PROXQP"] = self.options.with_proxqp
        tc.variables["WITH_QPOASES"] = self.options.with_qpoases
        tc.variables["WITH_SIMDE"] = self.options.with_proxqp
        tc.variables["WITH_SLEQP"] = self.options.with_sleqp
        tc.variables["WITH_SLICOT"] = False
        tc.variables["WITH_SNOPT"] = False
        tc.variables["WITH_SPRAL"] = self.options.with_spral
        tc.variables["WITH_SQIC"] = False
        tc.variables["WITH_SUNDIALS"] = self.options.with_sundials
        tc.variables["WITH_SUPERSCS"] = self.options.with_superscs
        tc.variables["WITH_THREAD"] = self.options.with_pthread
        tc.variables["WITH_TINYXML"] = self.options.with_tinyxml
        tc.variables["WITH_WORHP"] = False

        # TODO: create a CCI package for these vendored dependencies
        tc.variables["WITH_BUILD_ALPAQA"] = self.options.with_alpaqa
        tc.variables["WITH_BUILD_BLASFEO"] = self.options.with_blasfeo
        tc.variables["WITH_BUILD_BONMIN"] = self.options.with_bonmin
        tc.variables["WITH_BUILD_CSPARSE"] = self.options.with_csparse
        tc.variables["WITH_BUILD_DSDP"] = self.options.with_dsdp
        tc.variables["WITH_BUILD_FATROP"] = self.options.with_fatrop
        tc.variables["WITH_BUILD_HIGHS"] = self.options.with_highs
        tc.variables["WITH_BUILD_HPIPM"] = self.options.with_hpipm
        tc.variables["WITH_BUILD_HSL"] = self.options.with_hsl
        tc.variables["WITH_BUILD_PROXQP"] = self.options.with_proxqp
        tc.variables["WITH_BUILD_SIMDE"] = self.options.with_proxqp
        tc.variables["WITH_BUILD_SLEQP"] = self.options.with_sleqp
        tc.variables["WITH_BUILD_SPRAL"] = self.options.with_spral
        tc.variables["WITH_BUILD_SUNDIALS"] = self.options.with_sundials
        tc.variables["WITH_BUILD_SUPERSCS"] = self.options.with_superscs
        tc.variables["WITH_BUILD_TRLIB"] = self.options.with_sleqp

        tc.variables["WITH_BUILD_CBC"] = False
        tc.variables["WITH_BUILD_CLP"] = False
        tc.variables["WITH_BUILD_EIGEN3"] = False
        tc.variables["WITH_BUILD_IPOPT"] = False
        tc.variables["WITH_BUILD_LAPACK"] = False
        tc.variables["WITH_BUILD_METIS"] = False
        tc.variables["WITH_BUILD_MUMPS"] = False
        tc.variables["WITH_BUILD_OSQP"] = False
        tc.variables["WITH_BUILD_TINYXML"] = False
        tc.generate()

        venv = VirtualBuildEnv(self)
        venv.generate()

        if self.options.with_osqp:
            osqp = self.dependencies["osqp"].cpp_info
            osqp.includedirs.append(os.path.join(osqp.includedir, "osqp"))

        deps = CMakeDeps(self)
        deps.set_property("coin-mumps", "cmake_file_name", "MUMPS")
        deps.set_property("coin-mumps", "cmake_target_name", "mumps")
        deps.set_property("coin-cgl", "cmake_file_name", "COINCGL")
        deps.set_property("coin-cgl", "cmake_target_name", "cgl")
        deps.set_property("coin-osi", "cmake_file_name", "COINOSI")
        deps.set_property("coin-osi", "cmake_target_name", "osi")
        deps.set_property("coin-utils", "cmake_file_name", "COINUTILS")
        deps.set_property("coin-utils", "cmake_target_name", "coinutils")
        deps.set_property("eigen", "cmake_file_name", "EIGEN3")
        deps.set_property("eigen", "cmake_target_name", "eigen3")
        deps.set_property("opencl-headers", "cmake_file_name", "OpenCL")
        deps.set_property("metis", "cmake_file_name", "METIS")
        deps.set_property("metis", "cmake_target_name", "metis::metis")
        deps.set_property("osqp", "cmake_file_name", "OSQP")
        deps.set_property("osqp", "cmake_target_name", "osqp::osqp")
        deps.set_property("tinyxml", "cmake_file_name", "TINYXML")
        deps.set_property("tinyxml", "cmake_target_name", "tinyxml2::tinyxml2")
        deps.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        cmakelists = self.source_path.joinpath("CMakeLists.txt")
        content = cmakelists.read_text(encoding="utf-8")
        # Ensure the WITH_* dependencies are REQUIRED
        content = content.replace("find_package(${PKG})", "find_package(${PKG} REQUIRED)")
        # Fix external dependencies using -external suffix
        for dep in ["cbc", "cgl", "clp", "coinutils", "eigen3", "ipopt", "metis", "mumps", "osi", "osqp", "tinyxml"]:
            repl = dep if dep != "metis" else "metis::metis"
            content = content.replace(f"{dep}-external", repl)
        # Add find_package() for coin-utils for Bonmin
        if self.options.with_bonmin:
            content = content.replace("foreach(PKG ALPAQA ", "foreach(PKG COINCGL COINOSI COINUTILS ALPAQA ")
        cmakelists.write_text(content, encoding="utf-8")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "casadi")
        self.cpp_info.set_property("cmake_target_name", "casadi")
        self.cpp_info.set_property("pkg_config_name", "casadi")
        self.cpp_info.libs = ["casadi"]
        self.cpp_info.defines.append("CASADI_SNPRINTF=snprintf")
        self.runenv_info.define_path("CASADIPATH", os.path.join(self.package_folder, "lib"))

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("dl")
            if self.options.with_pthread:
                self.cpp_info.system_libs.append("pthread")

        if self.options.with_openmp:
            if is_msvc(self):
                openmp_flags = ["-openmp"]
            elif self.settings.compiler in ("gcc", "clang"):
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler == "apple-clang":
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]
            else:
                openmp_flags = []
            self.cpp_info.exelinkflags = openmp_flags
            self.cpp_info.sharedlinkflags = openmp_flags
