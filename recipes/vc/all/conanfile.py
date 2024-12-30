from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
import os

required_conan_version = ">=1.50.0"


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
        # https://github.com/VcDevel/Vc/blob/1.4.4/cmake/OptimizeForArchitecture.cmake
        "cpu_architecture": [
            "auto", "generic", "none", "x86-64", "x86-64-v2", "x86-64-v3", "x86-64-v4",
            # Intel
            "core", "merom", "penryn", "nehalem", "westmere", "sandy-bridge", "ivy-bridge", "haswell",
            "broadwell", "skylake", "skylake-xeon", "kaby-lake", "cannonlake", "silvermont", "goldmont",
            "knl", "atom",
            # AMD
            "k8", "k8-sse3", "barcelona", "istanbul", "magny-cours", "bulldozer", "interlagos",
            "piledriver", "AMD 14h", "AMD 16h", "zen", "zen3"
        ],
    }
    default_options = {
        "fPIC": True,
        "cpu_architecture": "sandy-bridge",  # sse sse2 sse3 ssse3 sse4.1 sse4.2 avx
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if is_apple_os(self):
            # sse sse2 sse3 ssse3 sse4.1 sse4.2, no avx
            self.options.cpu_architecture = "westmere"
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.cpu_architecture

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # https://github.com/openMVG/openMVG/blob/v2.1/src/cmakeFindModules/OptimizeForArchitecture.cmake
        tc.variables["TARGET_ARCHITECTURE"] = self.options.get_safe("cpu_architecture", "none")
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
