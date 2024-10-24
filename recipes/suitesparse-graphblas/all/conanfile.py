import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, Environment
from conan.tools.files import copy, get, rm, rmdir

required_conan_version = ">=1.53.0"


class SuiteSparseGraphBlasConan(ConanFile):
    name = "suitesparse-graphblas"
    description = "SuiteSparse:GraphBLAS: graph algorithms in the language of linear algebra"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://people.engr.tamu.edu/davis/GraphBLAS.html"
    topics = ("graph-algorithms", "mathematics", "sparse-matrix", "linear-algebra")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "compact": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "compact": True,
    }
    options_description = {
        "compact": ("If True, disable creation of many fast FactoryKernels at compile time. "
                    "The necessary kernels are compiled at run-time, via JIT, instead and "
                    "performance will be the same. JIT-compiled kernels are placed in <package_folder>/share. "
                    "Non-compact builds are significantly slower to compile and produce a larger library (both about 15x).")
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # note: C++ is used if CUDA is enabled
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # OpenMP is not used in any public headers
        self.requires("llvm-openmp/17.0.6")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _jit_cache_dir(self):
        return os.path.join(self.package_folder, "share")

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["GRAPHBLAS_COMPACT"] = self.options.compact
        tc.variables["GRAPHBLAS_USE_OPENMP"] = True
        tc.variables["GRAPHBLAS_USE_CUDA"] = False  # experimental, not ready for production as of 9.1.0
        tc.variables["SUITESPARSE_USE_CUDA"] = False
        tc.variables["SUITESPARSE_USE_STRICT"] = True  # require dependencies to be handled explicitly
        tc.variables["SUITESPARSE_USE_FORTRAN"] = False  # Fortran sources are translated to C instead
        tc.variables["SUITESPARSE_DEMOS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        env = Environment()
        env.define_path("GRAPHBLAS_CACHE_PATH", self._jit_cache_dir)
        env.vars(self).save_script("graphblas_jit_cache")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["graphblas"]
        self.cpp_info.set_property("cmake_file_name", "GraphBLAS")
        self.cpp_info.set_property("cmake_target_name", "SuiteSparse::GraphBLAS")
        if not self.options.shared:
            self.cpp_info.set_property("cmake_target_aliases", ["SuiteSparse::GraphBLAS_static"])
        self.cpp_info.set_property("pkg_config_name", "GraphBLAS")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])

        # FIXME: The JIT cache contains both input sources as well as the compilation cache.
        # The latter should not be located under the Conan package folder.
        self.buildenv_info.define_path("GRAPHBLAS_CACHE_PATH", self._jit_cache_dir)
        self.runenv_info.define_path("GRAPHBLAS_CACHE_PATH", self._jit_cache_dir)
