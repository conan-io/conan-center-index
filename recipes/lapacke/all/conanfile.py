from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import glob
import os

required_conan_version = ">=2.1"


class LapackeConan(ConanFile):
    name = "lapacke"
    description = "C language interface to LAPACK"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Reference-LAPACK/lapack"
    topics = ("lapack", "lapacke", "blas", "linear-algebra")
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

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("openblas/0.3.30")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_TESTING"] = False
        tc.variables["CBLAS"] = False
        tc.variables["LAPACKE"] = True
        tc.variables["LAPACKE_WITH_TMG"] = False
        tc.variables["USE_OPTIMIZED_BLAS"] = True
        tc.variables["USE_OPTIMIZED_LAPACK"] = True
        tc.variables["BUILD_INDEX64_EXT_API"] = False

        openblas_dep = self.dependencies["openblas"]
        openblas_libdir = os.path.join(openblas_dep.package_folder, "lib")
        openblas_lib = next((
            path for path in glob.glob(os.path.join(openblas_libdir, "*openblas*"))
            if os.path.isfile(path) and not path.lower().endswith((".dll", ".so", ".dylib"))
        ), None)
        if openblas_lib:
            openblas_lib = openblas_lib.replace("\\", "/")
            tc.variables["BLAS_LIBRARIES"] = openblas_lib
            tc.variables["LAPACK_LIBRARIES"] = openblas_lib

        if Version(self.version) < "3.13":
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"  # CMake 4 support
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="lapacke")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "lapacke")
        self.cpp_info.set_property("cmake_target_name", "lapacke::lapacke")
        self.cpp_info.set_property("pkg_config_name", "lapacke")

        self.cpp_info.libs = ["lapacke"]
        self.cpp_info.requires = ["openblas::openblas_component"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        if self.settings.os == "Windows":
            self.cpp_info.defines.extend(["HAVE_LAPACK_CONFIG_H", "LAPACK_COMPLEX_STRUCTURE"])
