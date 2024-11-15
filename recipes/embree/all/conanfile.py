from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.microsoft import check_min_vs
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import glob
import os

required_conan_version = ">=1.53.0"

class EmbreeConan(ConanFile):
    name = "embree"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("embree", "raytracing", "rendering")
    description = "Intel's collection of high-performance ray tracing kernels."
    homepage = "https://embree.github.io/"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "11",
            "clang": "7",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }

    @property
    def _has_sse_avx(self):
        return self.settings.arch in ["x86", "x86_64"]

    @property
    def _has_neon(self):
        return "arm" in self.settings.arch

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os != "Emscripten":
            self.requires("onetbb/2021.12.0")

    def validate(self):
        if not (self._has_sse_avx or self._has_neon):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support {self.settings.arch}")

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        compiler_version = Version(self.settings.compiler.version)
        if self.settings.compiler == "clang" and compiler_version < "4":
            raise ConanInvalidConfiguration("Clang < 4 is not supported")

        check_min_vs(self, 191)

        if self.settings.os == "Linux" and self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libc++":
            raise ConanInvalidConfiguration(f"{self.ref} cannot be built with clang libc++, use libstdc++ instead")

        if self.settings.compiler == "apple-clang" and not self.options.shared and compiler_version >= "9.0":
            raise ConanInvalidConfiguration(f"{self.ref} static with apple-clang >=9 and multiple ISA (simd) is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["EMBREE_STATIC_LIB"] = not self.options.shared
        tc.variables["BUILD_TESTING"] = False
        tc.variables["EMBREE_INSTALL_DEPENDENCIES"] = False
        tc.variables["EMBREE_TUTORIALS"] = False
        tc.variables["EMBREE_BACKFACE_CULLING"] = False 
        tc.variables["EMBREE_IGNORE_INVALID_RAYS"] = False
        tc.variables["EMBREE_ISPC_SUPPORT"] = False
        tc.variables["EMBREE_TASKING_SYSTEM"] = "INTERNAL" if is_apple_os(self) or self.settings.os == "Emscripten" else "TBB"
        tc.variables["EMBREE_MAX_ISA"] = "NONE"
        tc.variables["EMBREE_ISA_NEON"] = self._has_neon
        tc.variables["EMBREE_ISA_NEON2X"] = self._has_neon
        tc.variables["EMBREE_ISA_SSE2"] = self._has_sse_avx
        tc.variables["EMBREE_ISA_SSE42"] = self._has_sse_avx
        # For Emscripten disable TBB and all ISAs. It will compile only for SSE
        if self.settings.os == "Emscripten":
            tc.variables["EMBREE_ISA_AVX"] = self._has_sse_avx
            tc.variables["EMBREE_ISA_AVX2"] = self._has_sse_avx
            tc.variables["EMBREE_ISA_AVX512"] = self._has_sse_avx and not is_msvc(self)
            if is_msvc(self):
                tc.variables["USE_STATIC_RUNTIME"] = is_msvc_static_runtime(conanfile)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE.txt",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.command", os.path.join(self.package_folder))
        rm(self, "*.cmake", os.path.join(self.package_folder))
        rm(self, "embree-vars.sh", os.path.join(self.package_folder))
        rm(self, "embree-vars.csh", os.path.join(self.package_folder))

        # Remove MS runtime files
        for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
            rm(self, pattern=dll_pattern_to_remove, folder=os.path.join(self.package_folder, "bin"), recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["embree4"]
        if not self.options.shared:
            self.cpp_info.libs.extend(["sys", "math", "simd", "lexers", "tasking"])
            if self._has_sse_avx:
                self.cpp_info.libs.extend(["embree_sse42", "embree_avx", "embree_avx2"])
                if not is_msvc(self):
                    self.cpp_info.libs.append("embree_avx512")
            if self._has_neon:
                self.cpp_info.libs.extend(["embree_avx2"])

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
