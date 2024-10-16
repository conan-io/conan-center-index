import glob
import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, mkdir, rmdir, replace_in_file, save
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class SundialsConan(ConanFile):
    name = "sundials"
    license = "BSD-3-Clause"
    description = ("SUNDIALS is a family of software packages implemented with the goal of providing robust time integrators"
                   " and nonlinear solvers that can easily be incorporated into existing simulation codes.")
    topics = ("integrators", "ode", "non-linear-solvers")
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
        "with_cuda": [True, False],
        "with_ginkgo": [True, False],
        "with_klu": [True, False],
        "with_lapack": [True, False],
        "with_mpi": [True, False],
        "with_openmp": [True, False],
        "index_size": [32, 64],
        "precision": ["single", "double", "extended"],
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
        "with_cuda": False,
        "with_ginkgo": False,
        "with_klu": False,
        "with_lapack": True,
        "with_mpi": False,
        "with_openmp": False,
        "index_size": 64,
        "precision": "double",
    }

    short_paths = True

    def export_sources(self):
        copy(self, "*.cmake", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if Version(self.version) < "5.5.0":
            del self.options.with_cuda
            del self.options.with_ginkgo
            del self.options.with_klu
            del self.options.with_lapack
            del self.options.with_mpi
            del self.options.with_openmp
        elif Version(self.version) < "6.0":
            del self.options.with_ginkgo
        if not self.options.get_safe("with_cuda"):
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")
        if self.options.get_safe("with_mpi"):
            self.options["openmpi"].enable_cxx = True

    def package_id(self):
        # Ginkgo is only used in an INTERFACE component
        self.info.options.rm_safe("with_ginkgo")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Used in public headers:
        # - caliper: sundials/sundials_profiler.h
        # - cuda: sunmemory/sunmemory_cuda.h, nvector/nvector_cuda.h
        # - ginkgo: sunmatrix/sunmatrix_ginkgo.hpp, sunlinsol/sunlinsol_ginkgo.hpp
        # - klu: sunlinsol/sunlinsol_klu.h
        # - mpi: sundials/sundials_types.h, sundials/priv/sundials_mpi_errors_impl.h
        if self.options.get_safe("with_ginkgo"):
            self.requires("ginkgo/1.8.0", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_klu"):
            self.requires("suitesparse-klu/2.3.4", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_lapack"):
            self.requires("openblas/0.3.27")
        if self.options.get_safe("with_mpi"):
            self.requires("openmpi/4.1.6", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_openmp"):
            self.requires("openmp/system")

    def validate(self):
        if self.options.get_safe("with_klu") and self.options.precision != "double":
            # https://github.com/LLNL/sundials/blob/v7.1.1/cmake/tpl/SundialsKLU.cmake#L40
            raise ConanInvalidConfiguration("-o sundials/*:with_klu=True is only compatible with -o sundials/*:precision=double")
        if self.options.precision == "extended":
            # https://github.com/LLNL/sundials/blob/v7.1.1/cmake/tpl/SundialsGinkgo.cmake#L57
            # https://github.com/LLNL/sundials/blob/v7.1.1/cmake/tpl/SundialsLapack.cmake#L40
            for opt in ["with_cuda", "with_ginkgo", "with_lapack"]:
                if self.options.get_safe(opt):
                    raise ConanInvalidConfiguration(f"-o sundials/*:{opt}=True is not compatible with -o sundials/*:precision=extended")
        if self.options.get_safe("with_mpi") and not self.dependencies["openmpi"].options.get_safe("enable_cxx"):
            raise ConanInvalidConfiguration("-o openmpi/*:enable_cxx=True is required for -o sundials/*:with_mpi=True")

    def build_requirements(self):
        if Version(self.version) >= "7.0":
            self.tool_requires("cmake/[>=3.18 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _ginkgo_backends(self):
        if not self.options.get_safe("with_ginkgo"):
            return []
        backends = ["REF"]
        if self.dependencies["ginkgo"].options.cuda:
            backends.append("CUDA")
        if self.dependencies["ginkgo"].options.openmp:
            backends.append("OMP")
        return backends

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = CMakeToolchain(self)
        tc.variables["CMAKE_Fortran_COMPILER"] = ""
        tc.variables["EXAMPLES_ENABLE_C"] = False
        tc.variables["EXAMPLES_ENABLE_CXX"] = False
        tc.variables["EXAMPLES_INSTALL"] = False
        tc.variables["BUILD_BENCHMARKS"] = False
        tc.variables["SUNDIALS_TEST_UNITTESTS"] = False
        if Version(self.version) <= "5.4.0":
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.cache_variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = str(self.settings.build_type)

        # https://github.com/LLNL/sundials/blob/v7.1.1/cmake/SundialsBuildOptionsPre.cmake
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["SUNDIALS_INDEX_SIZE"] = self.options.index_size
        tc.variables["SUNDIALS_PRECISION"] = str(self.options.precision).upper()
        tc.variables["BUILD_ARKODE"] = self.options.build_arkode
        tc.variables["BUILD_CVODE"] = self.options.build_cvode
        tc.variables["BUILD_CVODES"] = self.options.build_cvodes
        tc.variables["BUILD_IDA"] = self.options.build_ida
        tc.variables["BUILD_IDAS"] = self.options.build_idas
        tc.variables["BUILD_KINSOL"] = self.options.build_kinsol

        # https://github.com/LLNL/sundials/blob/v7.1.1/cmake/SundialsTPLOptions.cmake
        tc.variables["ENABLE_MPI"] = self.options.get_safe("with_mpi", False)
        tc.variables["ENABLE_OPENMP"] = self.options.get_safe("with_openmp", False)
        tc.variables["ENABLE_CUDA"] = self.options.get_safe("with_cuda", False)
        tc.variables["ENABLE_HIP"] = False
        tc.variables["ENABLE_SYCL"] = False
        tc.variables["ENABLE_LAPACK"] = self.options.get_safe("with_lapack", False)
        tc.variables["LAPACK_WORKS"] = True
        tc.variables["ENABLE_GINKGO"] = self.options.get_safe("with_ginkgo", False)
        tc.variables["SUNDIALS_GINKGO_BACKENDS"] = ";".join(self._ginkgo_backends)
        tc.variables["GINKGO_WORKS"] = True
        tc.variables["ENABLE_MAGMA"] = False
        tc.variables["ENABLE_SUPERLUDIST"] = False
        tc.variables["ENABLE_SUPERLUMT"] = False
        tc.variables["ENABLE_KLU"] = self.options.get_safe("with_klu", False)
        tc.variables["KLU_WORKS"] = True
        tc.variables["ENABLE_HYPRE"] = False
        tc.variables["ENABLE_PETSC"] = False
        tc.variables["ENABLE_RAJA"] = False
        tc.variables["ENABLE_TRILINOS"] = False
        tc.variables["ENABLE_XBRAID"] = False
        tc.variables["ENABLE_ONEMKL"] = False
        tc.variables["ENABLE_CALIPER"] = False
        tc.variables["ENABLE_ADIAK"] = False
        tc.variables["ENABLE_KOKKOS"] = False

        # https://github.com/LLNL/sundials/blob/v7.1.1/cmake/SundialsBuildOptionsPost.cmake
        tc.variables["BUILD_SUNMATRIX_CUSPARSE"] = self.options.get_safe("with_cuda", False) and self.options.index_size == 32
        tc.variables["BUILD_SUNLINSOL_CUSOLVERSP"] = self.options.get_safe("with_cuda", False) and self.options.index_size == 32

        # Configure default LAPACK naming conventions for OpenBLAS.
        # Needed to avoid a Fortran compiler requirement to detect the correct name mangling scheme.
        # https://github.com/LLNL/sundials/blob/v7.1.1/cmake/SundialsSetupCompilers.cmake#L269-L360
        tc.variables["SUNDIALS_LAPACK_CASE"] = "lower"
        tc.variables["SUNDIALS_LAPACK_UNDERSCORES"] = "one"

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("suitesparse-klu", "cmake_target_name", "SUNDIALS::KLU")
        deps.generate()

    def _patch_sources(self):
        save(self, os.path.join(self.source_folder, "examples", "CMakeLists.txt"), "")
        if self.options.get_safe("with_ginkgo"):
            replace_in_file(self, os.path.join(self.source_folder, "cmake", "tpl", "SundialsGinkgo.cmake"),
                            "NO_DEFAULT_PATH", "")
        if self.options.get_safe("with_mpi"):
            replace_in_file(self, os.path.join(self.source_folder, "cmake", "tpl", "SundialsMPI.cmake"),
                            "find_package(MPI 2.0.0 REQUIRED)", "find_package(MPI REQUIRED)")

    def build(self):
        self._patch_sources()
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
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        fix_apple_shared_install_name(self)
        if self.options.get_safe("with_cuda"):
            copy(self, "conan-cuda-support.cmake", self.export_sources_folder, os.path.join(self.package_folder, "lib", "cmake", "sundials"))

    def package_info(self):
        # https://github.com/LLNL/sundials/blob/v7.1.1/cmake/SUNDIALSConfig.cmake.in
        if Version(self.version) >= "5.8.0":
            self.cpp_info.set_property("cmake_file_name", "SUNDIALS")

        suffix = ""
        if Version(self.version) >= "7.0" and self.settings.os == "Windows":
            suffix = "_shared" if self.options.shared else "_static"

        core_lib = None
        if Version(self.version) >= "7.0":
            core_lib = "core"
        elif Version(self.version) >= "5.8.0":
            core_lib = "generic"

        def _add_lib(name, requires=None, system_libs=None, interface=False):
            if Version(self.version) >= "5.8.0":
                component = self.cpp_info.components[name]
                component.set_property("cmake_target_name", f"SUNDIALS::{name}")
                component.set_property("cmake_target_aliases", [f"SUNDIALS::{name}_{'shared' if self.options.shared else 'static'}"])
            else:
                # For backward compatibility with old recipe versions
                component = self.cpp_info.components[f"sundials_{name}"]
                requires = [f"sundials_{r}" if "::" not in r else r for r in requires or []]
            if not interface:
                component.libs = [f"sundials_{name}{suffix}"]
            component.requires = requires or []
            component.system_libs = system_libs or []
            if core_lib and name != core_lib:
                component.requires.append(core_lib)
            if self.settings.os in ["Linux", "FreeBSD"]:
                component.system_libs.append("m")

        if core_lib:
            _add_lib(core_lib)
            if self.options.get_safe("with_mpi"):
                self.cpp_info.components[core_lib].requires.append("openmpi::openmpi")

        if self.options.build_arkode:
            _add_lib("arkode")
        if self.options.build_cvode:
            _add_lib("cvode")
        if self.options.build_cvodes:
            _add_lib("cvodes")
        if self.options.build_ida:
            _add_lib("ida")
        if self.options.build_idas:
            _add_lib("idas")
        if self.options.build_kinsol:
            _add_lib("kinsol")

        _add_lib("nvecserial")
        if self.options.get_safe("with_mpi"):
            _add_lib("nvecmanyvector", requires=["openmpi::openmpi"])
        if self.options.get_safe("with_openmp"):
            _add_lib("nvecopenmp", requires=["openmp::openmp"])

        _add_lib("sunmatrixband")
        _add_lib("sunmatrixdense")
        _add_lib("sunmatrixsparse")
        if self.options.get_safe("with_ginkgo"):
            _add_lib("sunmatrixginkgo", interface=True, requires=["ginkgo::ginkgo"])

        _add_lib("sunlinsolband", requires=["sunmatrixband"])
        _add_lib("sunlinsoldense", requires=["sunmatrixdense"])
        _add_lib("sunlinsolpcg")
        _add_lib("sunlinsolspbcgs")
        _add_lib("sunlinsolspfgmr")
        _add_lib("sunlinsolspgmr")
        _add_lib("sunlinsolsptfqmr")
        if self.options.get_safe("with_ginkgo"):
            _add_lib("sunmatrixginkgo", interface=True, requires=["ginkgo::ginkgo"])
            _add_lib("sunlinsolginkgo", interface=True, requires=["ginkgo::ginkgo"])
        if self.options.get_safe("with_klu"):
            _add_lib("sunlinsolklu", requires=["sunmatrixsparse", "suitesparse-klu::suitesparse-klu"])
        if self.options.get_safe("with_lapack"):
            _add_lib("sunlinsollapackband", requires=["sunmatrixband", "openblas::openblas"])
            _add_lib("sunlinsollapackdense", requires=["sunmatrixdense", "openblas::openblas"])

        _add_lib("sunnonlinsolfixedpoint")
        _add_lib("sunnonlinsolnewton")

        if self.options.get_safe("with_cuda"):
            system_libs = []
            if self.settings.os in ["Linux", "FreeBSD"]:
                system_libs.extend(["rt", "pthread", "dl"])
            if stdcpp_library(self):
                system_libs.append(stdcpp_library(self))

            _add_lib("nveccuda", system_libs=system_libs)
            if self.options.index_size == 32:
                _add_lib("sunmatrixcusparse", system_libs=system_libs) # + cusparse
                _add_lib("sunlinsolcusolversp", requires=["sunmatrixcusparse"], system_libs=system_libs) # + cusolver

            self.cpp_info.builddirs.append(os.path.join("lib", "cmake", "sundials"))
            cmake_module = os.path.join("lib", "cmake", "sundials", "conan-cuda-support.cmake")
            self.cpp_info.set_property("cmake_build_modules", [cmake_module])
            self.cpp_info.build_modules["cmake_find_package"] = [cmake_module]
            self.cpp_info.build_modules["cmake_find_package_multi"] = [cmake_module]
