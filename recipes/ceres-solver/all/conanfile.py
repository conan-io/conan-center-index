from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class CeressolverConan(ConanFile):
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
        "use_glog":  [True, False], #TODO Set to true once gflags with nothreads=False binaries are available. Using MINILOG has a big performance drawback.
        "use_gflags": [True, False, "deprecated"],
        "use_custom_blas": [True, False],
        "use_eigen_sparse": [True, False],
        "use_TBB": [True, False],
        "use_CXX11_threads": [True, False],
        "use_CXX11": [True, False],
        "use_schur_specializations": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_glog": False,
        "use_gflags": "deprecated",
        "use_custom_blas": True,
        "use_eigen_sparse": True,
        "use_TBB": False,
        "use_CXX11_threads": False,
        "use_CXX11": False,
        "use_schur_specializations": True,
    }

    @property
    def _min_cppstd(self):
        return "98" if Version(self.version) < "2.0.0" else "14"

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
        }.get(self._min_cppstd, {})

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) >= "2.0":
            del self.options.use_TBB
            del self.options.use_CXX11_threads
            del self.options.use_CXX11

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.use_gflags != "deprecated":
            self.output.warning("use_gflags option is deprecated")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)
        if self.options.use_glog:
            self.requires("glog/0.6.0", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("use_TBB"):
            self.requires("onetbb/2020.3")

    def package_id(self):
        del self.info.options.use_gflags

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MINIGLOG"] = not self.options.use_glog
        tc.variables["GFLAGS"] = False # useless for the lib itself, gflags is not a direct dependency
        tc.variables["SUITESPARSE"] = False
        tc.variables["CXSPARSE"] = False
        tc.variables["LAPACK"] = False
        tc.variables["SCHUR_SPECIALIZATIONS"] = self.options.use_schur_specializations
        tc.variables["CUSTOM_BLAS"] = self.options.use_custom_blas
        tc.variables["EIGENSPARSE"] = self.options.use_eigen_sparse
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_DOCUMENTATION"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_BENCHMARKS"] = False
        if is_msvc(self):
            tc.variables["MSVC_USE_STATIC_CRT"] = is_msvc_static_runtime(self)
        if Version(self.version) >= "2.1.0":
            tc.variables["CUDA"] = False
        if Version(self.version) >= "2.0.0":
            tc.variables["PROVIDE_UNINSTALL_TARGET"] = False
            if is_apple_os(self):
                tc.variables["ACCELERATESPARSE"] = True
        if Version(self.version) < "2.1.0":
            tc.variables["LIB_SUFFIX"] = ""
        if Version(self.version) < "2.0":
            tc.variables["CXX11"] = self.options.use_CXX11
            tc.variables["OPENMP"] = False
            tc.variables["TBB"] = self.options.use_TBB
            tc.variables["CXX11_THREADS"] = self.options.use_CXX11_threads
        tc.generate()

        CMakeDeps(self).generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "CMake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Ceres")
        self.cpp_info.set_property("cmake_target_name", "Ceres::ceres")

        libsuffix = ""
        if self.settings.build_type == "Debug":
            libsuffix = "-debug"
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["ceres"].libs = [f"ceres{libsuffix}"]
        self.cpp_info.components["ceres"].includedirs.append(os.path.join("include", "ceres"))
        if not self.options.use_glog:
            self.cpp_info.components["ceres"].includedirs.append(os.path.join("include", "ceres", "internal", "miniglog"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ceres"].system_libs.append("m")
            if self.options.get_safe("use_CXX11_threads", True):
                self.cpp_info.components["ceres"].system_libs.append("pthread")
        elif is_apple_os(self):
            if Version(self.version) >= "2":
                self.cpp_info.components["ceres"].frameworks.append("Accelerate")
        self.cpp_info.components["ceres"].requires = ["eigen::eigen"]
        if self.options.use_glog:
            self.cpp_info.components["ceres"].requires.append("glog::glog")
        if self.options.get_safe("use_TBB"):
            self.cpp_info.components["ceres"].requires.append("onetbb::onetbb")
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.components["ceres"].system_libs.append(libcxx)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Ceres"
        self.cpp_info.names["cmake_find_package_multi"] = "Ceres"
        self.cpp_info.components["ceres"].set_property("cmake_target_name", "Ceres::ceres")
