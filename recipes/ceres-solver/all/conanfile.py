import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save, replace_in_file
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.54.0"


class CeresSolverConan(ConanFile):
    name = "ceres-solver"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://ceres-solver.org/"
    description = (
        "Ceres Solver is an open source C++ library for modeling "
        "and solving large, complicated optimization problems"
    )
    topics = ("optimization", "non-linear least squares")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_cuda": [True, False],
        "use_eigen_metis": [True, False],
        "use_glog":  [True, False], # TODO Set to true once gflags with nothreads=False binaries are available. Using MINILOG has a big performance drawback.
        "use_lapack": [True, False],
        "use_eigen_sparse": [True, False],
        "use_suitesparse": [True, False],
        "use_accelerate": [True, False],
        "use_custom_blas": [True, False],
        "use_schur_specializations": [True, False],
        # Unavailable since v2.0.0
        "use_CXX11": [True, False],
        "use_CXX11_threads": [True, False],
        "use_OpenMP": [True, False],
        "use_TBB": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_cuda": False,
        "use_eigen_metis": True,
        "use_glog": True,
        "use_lapack": True,
        "use_eigen_sparse": True,
        "use_suitesparse": True,
        "use_accelerate": True,
        "use_custom_blas": True,
        "use_schur_specializations": True,
        "use_CXX11": False,
        "use_CXX11_threads": False,
        "use_OpenMP": True,
        "use_TBB": False,
    }
    options_description = {
        "use_cuda": "Enable CUDA support.",
        "use_glog": "If False, use a custom stripped down version of glog instead. Disabling glog has a big performance drawback.",
        "use_lapack": "Enable use of LAPACK directly within Ceres.",
        "use_eigen_sparse": "Enable Eigen as a sparse linear algebra library.",
        "use_suitesparse": "Enable SuiteSparse support.",
        "use_accelerate": "Enable use of sparse solvers in Apple's Accelerate framework.",
        "use_custom_blas": "Use handcoded BLAS routines (usually faster) instead of Eigen.",
        "use_schur_specializations": ("Enable template specializations for the fixed-size Schur complement based solvers. "
                                      "Can impact compilation time and memory usage and binary size."),
    }

    @property
    def _min_cppstd(self):
        if Version(self.version) >= "2.2.0":
            return "17"
        if Version(self.version) >= "2.0.0":
            return "14"
        return "98"

    @property
    def _compilers_minimum_version(self):
        return {
            "14": {
                "apple-clang": "5",
                "clang": "5",
                "gcc": "5",
                "msvc": "190",
                "Visual Studio": "14",
            },
            "17": {
                "apple-clang": "10",
                "clang": "7",
                "gcc": "8",
                "msvc": "191",
                "Visual Studio": "15",
            },
        }.get(self._min_cppstd, {})

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "ceres-conan-cuda-support.cmake", self.recipe_folder, self.export_sources_folder)
        copy(self, "FindSuiteSparse.cmake", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) >= "2.0":
            del self.options.use_TBB
            del self.options.use_OpenMP
            del self.options.use_CXX11_threads
            del self.options.use_CXX11
        if Version(self.version) < "2.2.0":
            del self.options.use_eigen_metis
        if Version(self.version) < "2.1.0":
            del self.options.use_cuda

        # https://github.com/ceres-solver/ceres-solver/blob/2.2.0/CMakeLists.txt#L168-L175
        if self.settings.os == "iOS":
            del self.options.use_glog
            del self.options.use_lapack
            del self.options.use_suitesparse

        if not is_apple_os(self) or self.version < "2.0.0":
            del self.options.use_accelerate

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _require_metis(self):
        if Version(self.version) < "2.2.0":
            return False
        return self.options.get_safe("use_eigen_metis") or self.options.get_safe("use_suitesparse")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)
        if self.options.get_safe("use_glog"):
            self.requires("glog/0.7.0", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("use_suitesparse"):
            self.requires("suitesparse-cholmod/5.2.1")
            self.requires("suitesparse-spqr/4.3.3")
        if self.options.get_safe("use_lapack"):
            self.requires("openblas/0.3.27")
        if self._require_metis:
            self.requires("metis/5.2.1")
        if self.options.get_safe("use_TBB"):
            self.requires("onetbb/2020.3")
        if self.options.get_safe("use_OpenMP"):
            self.requires("llvm-openmp/18.1.3")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

        if self.options.get_safe("use_cuda"):
            self.output.warning("CUDA support requires CUDA to be present on the system.")

        if self.options.get_safe("use_eigen_metis") and not self.options.use_eigen_sparse:
            raise ConanInvalidConfiguration("use_eigen_metis requires use_eigen_sparse=True")

        # https://github.com/ceres-solver/ceres-solver/blob/2.2.0/CMakeLists.txt#L203
        if self.options.use_eigen_sparse and self.dependencies["eigen"].options.MPL2_only:
            raise ConanInvalidConfiguration("use_eigen_sparse=True requires eigen with MPL2_only=False")

        if self.options.get_safe("use_lapack") and not self.dependencies["openblas"].options.build_lapack:
            raise ConanInvalidConfiguration("use_lapack=True requires openblas with build_lapack=True")

    def build_requirements(self):
        if Version(self.version) >= "2.2.0":
            self.tool_requires("cmake/[>=3.18 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_DOCUMENTATION"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_BENCHMARKS"] = False
        tc.variables["PROVIDE_UNINSTALL_TARGET"] = False

        tc.variables["CUSTOM_BLAS"] = self.options.use_custom_blas
        tc.variables["EIGENSPARSE"] = self.options.use_eigen_sparse
        tc.variables["GFLAGS"] = False # useless for the lib itself, gflags is not a direct dependency
        tc.variables["LAPACK"] = self.options.get_safe("use_lapack", False)
        tc.variables["MINIGLOG"] = not self.options.get_safe("use_glog", False)
        tc.variables["SCHUR_SPECIALIZATIONS"] = self.options.use_schur_specializations
        tc.variables["SUITESPARSE"] = self.options.get_safe("use_suitesparse", False)

        # IOS_DEPLOYMENT_TARGET variable was added to iOS.cmake file in 1.12.0 version
        if self.settings.os == "iOS":
            tc.variables["IOS_DEPLOYMENT_TARGET"] = self.settings.os.version

        ceres_version = Version(self.version)
        if ceres_version >= "2.2.0":
            tc.variables["USE_CUDA"] = self.options.get_safe("use_cuda", False)
        elif ceres_version >= "2.1.0":
            tc.variables["CUDA"] = self.options.get_safe("use_cuda", False)
        if ceres_version >= "2.2.0":
            tc.variables["EIGENMETIS"] = self.options.use_eigen_metis
        if ceres_version >= "2.0.0":
            tc.variables["ACCELERATESPARSE"] = self.options.get_safe("use_accelerate", False)

        if ceres_version < "2.2.0":
            tc.variables["CXSPARSE"] = False
            tc.variables["MSVC_USE_STATIC_CRT"] = is_msvc_static_runtime(self)
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        if ceres_version < "2.1.0":
            tc.variables["LIB_SUFFIX"] = ""
        if ceres_version < "2.0.0":
            tc.variables["CXX11"] = self.options.use_CXX11
            tc.variables["OPENMP"] = not self.options.use_OpenMP
            tc.variables["TBB"] = self.options.use_TBB
            tc.variables["CXX11_THREADS"] = self.options.use_CXX11_threads
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("openblas", "cmake_file_name", "LAPACK")
        deps.set_property("metis", "cmake_file_name", "METIS")
        deps.set_property("metis", "cmake_target_name", "METIS::METIS")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        copy(self, "FindSuiteSparse.cmake", self.export_sources_folder, os.path.join(self.source_folder, "cmake"))
        if Version(self.version) < "2.0":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "list(APPEND CERES_COMPILE_OPTIONS CERES_USE_OPENMP)",
                            "list(APPEND CERES_COMPILE_OPTIONS CERES_USE_OPENMP)\n"
                            "link_libraries(OpenMP::OpenMP_CXX)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "CMake"))
        copy(self, "ceres-conan-cuda-support.cmake", self.export_sources_folder, os.path.join(self.package_folder, "lib", "cmake"))
        self._create_cmake_module_variables(os.path.join(self.package_folder, self._module_variables_file_rel_path))

    def _create_cmake_module_variables(self, module_file):
        # Define several variables of upstream CMake config file which are not
        # defined out of the box by CMakeDeps.
        # See https://github.com/ceres-solver/ceres-solver/blob/master/cmake/CeresConfig.cmake.in
        content = textwrap.dedent(f"""\
            set(CERES_FOUND TRUE)
            set(CERES_VERSION {self.version})
            if(NOT DEFINED CERES_LIBRARIES)
                set(CERES_LIBRARIES Ceres::ceres)
            endif()
        """)
        save(self, module_file, content)

    @property
    def _module_variables_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Ceres")

        libsuffix = "-debug" if self.settings.build_type == "Debug" else ""
        self.cpp_info.components["ceres"].set_property("cmake_target_name", "Ceres::ceres")
        # see https://github.com/ceres-solver/ceres-solver/blob/2.2.0/cmake/CeresConfig.cmake.in#L334-L340
        self.cpp_info.components["ceres"].set_property("cmake_target_aliases", ["ceres"])
        self.cpp_info.components["ceres"].libs = [f"ceres{libsuffix}"]
        if not self.options.use_glog:
            self.cpp_info.components["ceres"].includedirs.append(os.path.join("include", "ceres", "internal", "miniglog"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ceres"].system_libs.extend(["m", "pthread"])
        if self.options.get_safe("use_accelerate"):
            self.cpp_info.components["ceres"].frameworks.append("Accelerate")

        requires = ["eigen::eigen"]
        if self.options.get_safe("use_glog"):
            requires.append("glog::glog")
        if self.options.get_safe("use_suitesparse"):
            requires.append("suitesparse-cholmod::suitesparse-cholmod")
            requires.append("suitesparse-spqr::suitesparse-spqr")
        if self.options.get_safe("use_lapack"):
            requires.append("openblas::openblas")
        if self._require_metis:
            requires.append("metis::metis")
        if self.options.get_safe("use_TBB"):
            requires.append("onetbb::onetbb")
        if self.options.get_safe("use_OpenMP"):
            requires.append("llvm-openmp::llvm-openmp")
        self.cpp_info.components["ceres"].requires = requires

        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.components["ceres"].system_libs.append(libcxx)

        if self.options.get_safe("use_cuda"):
            if Version(self.version) >= "2.2.0":
                self.cpp_info.components["ceres_cuda_kernels"].set_property("cmake_target_name", "Ceres::ceres_cuda_kernels")
                self.cpp_info.components["ceres_cuda_kernels"].libs.append(f"ceres_cuda_kernels{libsuffix}")
                if not self.options.shared:
                    self.cpp_info.components["ceres"].requires.append("ceres_cuda_kernels")

        cmake_modules = [self._module_variables_file_rel_path]
        if self.options.get_safe("use_cuda"):
            cmake_modules.append(os.path.join("lib", "cmake", "ceres-conan-cuda-support.cmake"))
        self.cpp_info.set_property("cmake_build_modules", cmake_modules)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Ceres"
        self.cpp_info.names["cmake_find_package_multi"] = "Ceres"
        self.cpp_info.components["ceres"].build_modules["cmake_find_package"] = cmake_modules
        self.cpp_info.components["ceres"].build_modules["cmake_find_package_multi"] = cmake_modules
