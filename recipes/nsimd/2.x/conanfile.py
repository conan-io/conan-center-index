import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, replace_in_file

required_conan_version = ">=1.33.0"


class NsimdConan(ConanFile):
    name = "nsimd"
    homepage = "https://github.com/agenium-scale/nsimd"
    description = "Agenium Scale vectorization library for CPUs and GPUs"
    topics = ("hpc", "neon", "cuda", "avx", "simd", "avx2", "sse2", "aarch64", "avx512", "sse42", "rocm", "sve", "neon128")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # This used only when building the library.
        # Most functionality is header only.
        "simd": [None, "cpu", "sse2", "sse42", "avx", "avx2", "avx512_knl", "avx512_skylake", "neon128", "aarch64", "sve", "sve128", "sve256", "sve512", "sve1024", "sve2048", "cuda", "rocm"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "simd": None
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # Most of the library is header only.
        # cpp files do not use STL.
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.simd:
            tc.variables["simd"] = self.options.simd
        if self.settings.arch == "armv7hf":
            tc.variables["NSIMD_ARM32_IS_ARMEL"] = False
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        tc.generate()

    def _patch_sources(self):
        # nsimd.h uses size_t in its C++20 block but only includes <concepts>,
        # which no longer pulls in <cstddef> with newer libstdc++ (GCC 14+).
        # Fixed upstream in 3.0.1.
        if self.version == "2.2":
            replace_in_file(self, os.path.join(self.source_folder, "include", "nsimd", "nsimd.h"),
                            "  #include <concepts>",
                            "  #include <concepts>\n  #include <cstddef>")
        # nsimd 3.0.1 misspells NSIMD_CXX in the SSE4.2 block, so C++20 builds
        # targeting SSE4.2 never define nsimd::simd_ext_c.
        if self.version == "3.0.1":
            replace_in_file(self, os.path.join(self.source_folder, "include", "nsimd", "nsimd.h"),
                            "#if nsIMD_CXX >= 2020",
                            "#if NSIMD_CXX >= 2020")
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
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
