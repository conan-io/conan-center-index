import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=1.54.0"


class OptimLibConan(ConanFile):
    name = "optimlib"
    description = "OptimLib: a lightweight C++ library of numerical optimization methods for nonlinear functions"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kthohr/optim"
    topics = ("numerical-optimization", "optimization", "automatic-differentiation", "evolutionary-algorithms")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
        "linear_alg_lib": ["arma", "eigen"],
        "floating_point_type": ["float", "double"],
        "with_openmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
        "linear_alg_lib": "eigen",
        "floating_point_type": "double",
        "with_openmp": False,
    }

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            self.package_type = "header-library"
            self.options.rm_safe("shared")
            self.options.rm_safe("fPIC")
        elif self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.linear_alg_lib == "arma":
            self.requires("armadillo/12.6.4", transitive_headers=True, transitive_libs=True)
        elif self.options.linear_alg_lib == "eigen":
            self.requires("eigen/3.4.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_openmp:
            # '#pragma omp' is used in public headers
            self.requires("openmp/system", transitive_headers=True, transitive_libs=True)

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        if self.settings.os == "Windows":
            # "Use of this library with Windows-based systems, with or without MSVC, is not supported."
            raise ConanInvalidConfiguration("Windows is not supported")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["base_matrix_ops"], strip_root=True,
            destination=os.path.join(self.source_folder, "include", "BaseMatrixOps"))

    def generate(self):
        if not self.options.header_only:
            tc = CMakeToolchain(self)
            tc.variables["OPTIM_LINEAR_ALG_LIB"] = str(self.options.linear_alg_lib)
            tc.variables["OPTIM_PARALLEL"] = self.options.with_openmp
            tc.variables["OPTIM_FPN_TYPE"] = str(self.options.floating_point_type)
            tc.generate()
            deps = CMakeDeps(self)
            deps.generate()

    def build(self):
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "NOTICE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if self.options.header_only:
            self.run(f"./configure --header-only-version", cwd=self.source_folder)
            include_dir = os.path.join(self.source_folder, "header_only_version")
            copy(self, "*.hpp", include_dir, os.path.join(self.package_folder, "include"))
            copy(self, "*.ipp", include_dir, os.path.join(self.package_folder, "include"))
        else:
            cmake = CMake(self)
            cmake.install()

    def package_info(self):
        # Unofficial CMake file and target
        self.cpp_info.set_property("cmake_file_name", "OptimLib")
        self.cpp_info.set_property("cmake_target_name", "OptimLib::OptimLib")

        if not self.options.header_only:
            self.cpp_info.libs = ["optim"]

        if self.options.linear_alg_lib == "arma":
            self.cpp_info.defines.append("OPTIM_ENABLE_ARMA_WRAPPERS")
            if self.settings.build_type not in ["Debug", "RelWithDebInfo"]:
                self.cpp_info.defines.append("ARMA_NO_DEBUG")
        elif self.options.linear_alg_lib == "eigen":
            self.cpp_info.defines.append("OPTIM_ENABLE_EIGEN_WRAPPERS")
        self.cpp_info.defines.append(f"OPTIM_FPN_TYPE={self.options.floating_point_type}")
