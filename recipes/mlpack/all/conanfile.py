from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class MlpackConan(ConanFile):
    name = "mlpack"
    description = "mlpack: a fast, header-only C++ machine learning library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mlpack/mlpack"
    topics = ("machine-learning", "deep-learning", "regression", "nearest-neighbor-search", "scientific-computing", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Using version ranges since this is a header-only library
        # Minimum versions based on https://github.com/mlpack/mlpack/blob/4.3.0/CMakeLists.txt#L21-L28
        self.requires("armadillo/[>=9.800 <13]")
        self.requires("cereal/[>=1.1.2 <2]")
        self.requires("ensmallen/[>=2.10.0 <3]")
        self.requires("stb/[*]")
        # TODO: MSVC OpenMP is not compatible, enable for MSVC after #22353
        if not is_msvc(self):
            self.requires("llvm-openmp/[*]")
        # Should match the version used by Armadillo
        self.requires("openblas/[*]")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if not self.dependencies["armadillo"].options.use_blas or not self.dependencies["armadillo"].options.use_lapack:
            raise ConanInvalidConfiguration("mlpack requires armadillo to be built with BLAS and LAPACK support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_OPENMP"] = not is_msvc(self)
        tc.variables["BUILD_CLI_EXECUTABLES"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("armadillo", "cmake_file_name", "Armadillo")
        deps.set_property("cereal", "cmake_file_name", "cereal")
        deps.set_property("ensmallen", "cmake_file_name", "Ensmallen")
        deps.set_property("stb", "cmake_file_name", "StbImage")
        deps.generate()

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # Do not download dependencies when cross-compiling
        replace_in_file(self, cmakelists, "set(DOWNLOAD_DEPENDENCIES ON)", "")
        replace_in_file(self, cmakelists, "ARMADILLO_", "Armadillo_")
        replace_in_file(self, cmakelists, "CEREAL_", "cereal_")
        replace_in_file(self, cmakelists, "ENSMALLEN_", "Ensmallen_")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))

    @property
    def _openmp_flags(self):
        # Based on https://github.com/Kitware/CMake/blob/v3.28.1/Modules/FindOpenMP.cmake#L104-L135
        if self.settings.compiler == "clang":
            return ["-fopenmp=libomp"]
        elif self.settings.compiler == "apple-clang":
            return ["-Xclang", "-fopenmp"]
        elif self.settings.compiler == "gcc":
            return ["-fopenmp"]
        elif self.settings.compiler == "intel-cc":
            return ["-Qopenmp"]
        elif self.settings.compiler == "sun-cc":
            return ["-xopenmp"]
        elif is_msvc(self):
            return ["-openmp:llvm"]
        return None

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mlpack")
        self.cpp_info.set_property("cmake_target_name", "mlpack::mlpack")
        self.cpp_info.set_property("pkg_config_name", "mlpack")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])

        if self.settings.get_safe("compiler.libcxx") in ["libstdc++", "libstdc++11"]:
            self.cpp_info.system_libs.append("atomic")

        self.cpp_info.cflags = self._openmp_flags
        self.cpp_info.cxxflags = self._openmp_flags
