from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
import os

required_conan_version = ">=1.50.0"

# https://github.com/VcDevel/Vc/blob/1.4.4/cmake/OptimizeForArchitecture.cmake#L493-L513
cpu_features = [
    "sse2",
    "sse3",
    "ssse3",
    "sse4_1",
    "sse4_2",
    "sse4a",
    "avx",
    "fma",
    "bmi2",
    "avx2",
    "xop",
    "fma4",
    "avx512f",
    "avx512vl",
    "avx512pf",
    "avx512er",
    "avx512cd",
    "avx512dq",
    "avx512bw",
    "avx512ifma",
    "avx512vbmi",
]

class VcConan(ConanFile):
    name = "vc"
    description = "SIMD Vector Classes for C++."
    license = "BSD-3-Clause"
    topics = ("simd", "vectorization", "parallel", "sse", "avx", "neon")
    homepage = "https://github.com/VcDevel/Vc"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    # See https://github.com/VcDevel/Vc/blob/1.4.4/cmake/OptimizeForArchitecture.cmake for details.
    # Defaults are based on Steam Hardware survey as of 2024-05 and the common subset of features supported by both
    # Intel Skylake (2015+) and AMD Piledriver (2012+) architectures.
    options.update({f"use_{feature}": [True, False] for feature in cpu_features})
    default_options.update({f"use_{feature}": False for feature in cpu_features})
    default_options.update({
        "use_sse2": True,
        "use_sse3": True,
        "use_ssse3": True,
        "use_sse4_1": True,
        "use_sse4_2": True,
        "use_sse4a": False,
        "use_avx": True,
        "use_fma": True,
    })

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            for feature in cpu_features:
                self.options.rm_safe(f"use_{feature}")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Set TARGET_ARCHITECTURE to generic to avoid automatic detection of the target architecture.
        tc.variables["TARGET_ARCHITECTURE"] = "generic"
        for feature in cpu_features:
            tc.variables[f"USE_{feature.upper()}"] = self.options.get_safe(f"use_{feature}", False)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, 'AddCompilerFlag("-fPIC" CXX_FLAGS libvc_compile_flags)', "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Vc")
        self.cpp_info.set_property("cmake_target_name", "Vc::Vc")
        self.cpp_info.libs = ["Vc"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Vc"
        self.cpp_info.names["cmake_find_package_multi"] = "Vc"
