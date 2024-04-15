from conan import ConanFile
from conan.tools.files import get, copy, rm, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class OsqpConan(ConanFile):
    name = "osqp"
    package_type = "library"
    description = "The OSQP (Operator Splitting Quadratic Program) solver is a numerical optimization package."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://osqp.org/"
    topics = ("machine-learning", "control", "optimization", "svm", "solver", "lasso", "portfolio-optimization",
              "numerical-optimization", "quadratic-programming", "convex-optimization", "model-predictive-control")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "printing": [True, False],
        "profiling": [True, False],
        "ctrlc": [True, False],
        "dfloat": [True, False],
        "dlong": [True, False],
        "coverage": [True, False],
        "mkl_paradisio": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "printing": True,
        "profiling": True,
        "ctrlc": True,
        "dfloat": False,
        "dlong": True,
        "coverage": False,
        "mkl_paradisio": True
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        strip_root = self.version == "0.6.2"
        get(self, **self.conan_data["sources"][self.version], strip_root=strip_root)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['UNITTESTS'] = not self.conf.get("tools.build:skip_test", default=True, check_type=bool)
        tc.variables["PRINTING"] = self.options.printing
        tc.variables["PROFILING"] = self.options.profiling
        tc.variables["CTRLC"] = self.options.ctrlc
        tc.variables["DFLOAT"] = self.options.dfloat
        tc.variables["DLONG"] = self.options.dlong
        tc.variables["COVERAGE"] = self.options.coverage
        tc.variables["ENABLE_MKL_PARDISO"] = self.options.mkl_paradisio
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        if self.settings.os == "Windows":
            if self.options.shared:
                rm(self, "qdldl.dll", os.path.join(self.package_folder, "bin"))
            else:
                rmdir(self, os.path.join(self.package_folder, "bin"))
        else:
            if self.options.shared:
                rm(self, "*.a", os.path.join(self.package_folder, "lib"))
            else:
                rm(self, "*.so", os.path.join(self.package_folder, "lib"))
                rm(self, "*.dylib", os.path.join(self.package_folder, "lib"))

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "include", "qdldl"))
        rm(self, "*qdldl.*", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "osqp")
        self.cpp_info.set_property("cmake_target_name", "osqp::osqp")
        self.cpp_info.libs = ["osqp"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("rt")
            self.cpp_info.system_libs.append("dl")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "osqp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "osqp"
        self.cpp_info.names["cmake_find_package"] = "osqp"
        self.cpp_info.names["cmake_find_package_multi"] = "osqp"
