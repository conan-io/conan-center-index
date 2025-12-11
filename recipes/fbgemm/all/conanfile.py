from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, check_min_cstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
import os

required_conan_version = ">=2.4"


class FbgemmConan(ConanFile):
    name = "fbgemm"
    description = (
        "Facebook General Matrix Multiplication is a low-precision, high-performance matrix-matrix multiplication"
    )
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pytorch/FBGEMM"
    topics = ("convolution", "matrix", "multiplication", "quantization", "performance")
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
    implements = ["auto_shared_fpic"]
    languages = "C", "C++"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpuinfo/[>=cci.20250321]", transitive_headers=True, transitive_libs=True)
        self.requires("asmjit/cci.20240531", transitive_headers=True, transitive_libs=True)

    def validate(self):
        check_min_cppstd(self, 17)
        if self.settings.get_safe("compiler.cstd"):
            check_min_cstd(self, 99)
        if "arm" in self.settings.arch or self.settings.arch == "x86":
            raise ConanInvalidConfiguration("fbgemm is not supported on ARM or x86 architectures")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["FBGEMM_BUILD_TESTS"] = False
        tc.cache_variables["FBGEMM_BUILD_BENCHMARKS"] = False
        tc.cache_variables["FBGEMM_BUILD_FBGEMM_GPU"] = False  # Off by default, consider enabling in the future
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("cpuinfo", "cmake_target_name", "cpuinfo")
        deps.set_property("asmjit", "cmake_target_name", "asmjit")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fbgemmLibrary")
        self.cpp_info.set_property("cmake_target_name", "fbgemm")
        self.cpp_info.libs = ["fbgemm"]

        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines = ["FBGEMM_STATIC"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
        if self.settings.compiler in ("gcc", "clang"):
            self.cpp_info.sharedlinkflags.append("-fopenmp")
            self.cpp_info.exelinkflags.append("-fopenmp")
