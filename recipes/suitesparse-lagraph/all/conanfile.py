import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, rm, rmdir, copy

required_conan_version = ">=1.53.0"


class SuiteSparseLagraphConan(ConanFile):
    name = "suitesparse-lagraph"
    description = "LAGraph: Library plus test harness for collecting algorithms that use GraphBLAS"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://lagraph.readthedocs.io/en/latest/"
    topics = ("graph-algorithms", "mathematics", "sparse-matrix", "linear-algebra")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

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

    def requirements(self):
        self.requires("suitesparse-graphblas/9.1.0", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["SUITESPARSE_USE_OPENMP"] = True
        tc.variables["SUITESPARSE_USE_CUDA"] = False
        tc.variables["SUITESPARSE_DEMOS"] = False
        tc.variables["SUITESPARSE_USE_FORTRAN"] = False  # Fortran sources are translated to C instead
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "LAGraph"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", os.path.join(self.source_folder, "Doc"), os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LAGraph")

        self.cpp_info.components["LAGraph"].set_property("cmake_target_name", "SuiteSparse::LAGraph")
        if not self.options.shared:
            self.cpp_info.components["KLU"].set_property("cmake_target_aliases", ["SuiteSparse::LAGraph_static"])
        self.cpp_info.components["LAGraph"].set_property("pkg_config_name", "LAGraph")
        self.cpp_info.components["LAGraph"].libs = ["lagraph"]
        self.cpp_info.components["LAGraph"].requires = ["suitesparse-graphblas::suitesparse-graphblas"]
        self.cpp_info.components["LAGraph"].includedirs.append(os.path.join("include", "suitesparse"))
        self.cpp_info.components["LAGraph"].defines.append("LG_DLL")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["LAGraph"].system_libs.extend(["m", "pthread"])

        self.cpp_info.components["LAGraphX"].set_property("cmake_target_name", "SuiteSparse::LAGraphX")
        if not self.options.shared:
            self.cpp_info.components["KLU"].set_property("cmake_target_aliases", ["SuiteSparse::LAGraph_static"])
        self.cpp_info.components["LAGraphX"].set_property("pkg_config_name", "LAGraphX")
        self.cpp_info.components["LAGraphX"].libs = ["lagraphx"]
        self.cpp_info.components["LAGraphX"].requires = ["LAGraph"]

