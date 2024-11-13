from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, replace_in_file
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
    no_copy_source = True

    @property
    def _min_cppstd(self):
        if Version(self.version) >= "4.4.0":
            return 17
        if is_msvc(self):
            return 17
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
        self.requires("armadillo/12.6.4")
        self.requires("cereal/1.3.2")
        self.requires("ensmallen/2.21.0")
        self.requires("stb/cci.20230920")
        # TODO: MSVC OpenMP is not compatible, enable for MSVC after #22353
        if not is_msvc(self):
            self.requires("llvm-openmp/17.0.6")

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

    def _configure_headers(self):
        # https://github.com/mlpack/mlpack/blob/4.3.0/src/mlpack/config.hpp
        config_hpp = os.path.join(self.package_folder, "include", "mlpack", "config.hpp")
        replace_in_file(self, config_hpp, "// #define MLPACK_HAS_STB", "#define MLPACK_HAS_STB")
        replace_in_file(self, config_hpp, "// #define MLPACK_HAS_NO_STB_DIR", "// #define MLPACK_HAS_NO_STB_DIR")

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*",
             os.path.join(self.source_folder, "src"),
             os.path.join(self.package_folder, "include"),
             excludes=["mlpack/bindings/*", "mlpack/tests/*", "mlpack/CMakeLists.txt"])
        self._configure_headers()

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

        # FIXME: Review this flags assignment. LLVM-OpenMP is already defining these ones.
        #        Do we want to depend on llvm-openmp? Only for apple-clang?
        #        For more info, see this comment https://github.com/conan-io/conan-center-index/pull/22353#issuecomment-2214593855
        flags = []
        # Based on https://github.com/Kitware/CMake/blob/v3.28.1/Modules/FindOpenMP.cmake#L104-L135
        if self.settings.compiler == "clang":
            flags = ["-fopenmp=libomp"]
        elif self.settings.compiler == "gcc":
            flags = ["-fopenmp"]
            if self.settings.os == "Windows":
                flags.append("-Wa,-mbig-obj")
        elif self.settings.compiler == "sun-cc":
            flags = ["-xopenmp"]
        elif is_msvc(self):
        # https://github.com/mlpack/mlpack/blob/4.3.0/CMakeLists.txt#L164-L175
            flags = ["-openmp:llvm", "/bigobj", "/Zm200", "/Zc:__cplusplus"]
        if flags:
            self.cpp_info.cflags = flags
            self.cpp_info.cxxflags = flags
