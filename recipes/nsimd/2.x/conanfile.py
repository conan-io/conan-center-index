import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, export_conandata_patches, get, replace_in_file

required_conan_version = ">=1.53.0"


class NsimdConan(ConanFile):
    name = "nsimd"
    description = "Agenium Scale vectorization library for CPUs and GPUs"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/agenium-scale/nsimd"
    topics = ("hpc", "neon", "cuda", "avx", "simd", "avx2", "sse2",
              "aarch64", "avx512", "sse42", "rocm", "sve", "neon128")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # This used only when building the library.
        # Most functionality is header only.
        "simd": [None, "cpu", "sse2", "sse42", "avx", "avx2", "avx512_knl",
                 "avx512_skylake", "neon128", "aarch64", "sve", "sve128",
                 "sve256", "sve512", "sve1024", "sve2048", "cuda", "rocm"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "simd": None,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # Most of the library is header only.
        # cpp files do not use STL.
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.simd:
            tc.variables["simd"] = self.options.simd
        if self.settings.arch == "armv7hf":
            tc.variables["NSIMD_ARM32_IS_ARMEL"] = False
        tc.generate()

    def _patch_sources(self):
        cmakefile_path = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakefile_path,
                        " SHARED ",
                        " ")
        replace_in_file(self, cmakefile_path,
                        "RUNTIME DESTINATION lib",
                        "RUNTIME DESTINATION bin")
        replace_in_file(self, cmakefile_path,
                        "set_property(TARGET ${o} PROPERTY POSITION_INDEPENDENT_CODE ON)",
                        "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["nsimd_cpu"]
