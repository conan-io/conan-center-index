import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class VlfeatConan(ConanFile):
    name = "vlfeat"
    description = ("The VLFeat library implements popular computer vision algorithms specializing in "
                   "image understanding and local features extraction and matching.")
    license = "BSD 2-Clause"
    homepage = "https://www.vlfeat.org"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("computer-vision", "image-features")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threads": [True, False],
        "openmp": [True, False],
        "sse2": [True, False],
        "avx": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threads": True,
        "openmp": True,
        "sse2": True,
        "avx": False,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.sse2
            del self.options.avx

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.openmp:
            # Used only in .c files
            self.requires("llvm-openmp/18.1.8")

    def validate(self):
        if is_msvc(self) and not self.options.shared:
            # vlfeat function calls crash with STATUS_ACCESS_VIOLATION in test_package
            raise ConanInvalidConfiguration("vlfeat does not support static linkage with MSVC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_THREADS"] = self.options.threads
        tc.variables["ENABLE_OPENMP"] = self.options.openmp
        tc.variables["ENABLE_SSE2"] = self.options.get_safe("sse2", False)
        tc.variables["ENABLE_AVX"] = self.options.get_safe("avx", False)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["vl"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
            if self.options.threads:
                self.cpp_info.system_libs.append("pthread")

        if not self.options.get_safe("sse2"):
            self.cpp_info.defines.append("VL_DISABLE_SSE2")
        if not self.options.get_safe("avx"):
            self.cpp_info.defines.append("VL_DISABLE_AVX")
        if not self.options.threads:
            self.cpp_info.defines.append("VL_DISABLE_THREADS")
