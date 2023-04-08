from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import export_conandata_patches, apply_conandata_patches, get, copy, rm, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

import os
import glob

required_conan_version = ">=1.53.0"


class CBlosc2Conan(ConanFile):
    name = "c-blosc2"
    description = "A fast, compressed, persistent binary data store library for C."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Blosc/c-blosc2"
    topics = ("c-blosc", "blosc", "compression")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "simd_intrinsics": [None, "sse2", "avx2"],
        "with_lz4": [True, False],
        "with_zlib": [None, "zlib", "zlib-ng", "zlib-ng-compat"],
        "with_zstd": [True, False],
        "with_plugins": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "simd_intrinsics": "avx2",
        "with_lz4": True,
        "with_zlib": "zlib",
        "with_zstd": True,
        "with_plugins": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.simd_intrinsics

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

        # c-blosc2 uses zlib-ng with zlib compat options.
        if self.options.with_zlib == "zlib-ng-compat":
            self.options["zlib-ng"].zlib_compat = True
        elif self.options.with_zlib == "zlib-ng":
            self.options["zlib-ng"].zlib_compat = False

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_lz4:
            self.requires("lz4/1.9.4")
        if self.options.with_zlib in ["zlib-ng", "zlib-ng-compat"]:
            self.requires("zlib-ng/2.0.6")
        elif self.options.with_zlib == "zlib":
            self.requires("zlib/1.2.13")
        if self.options.with_zstd:
            self.requires("zstd/1.5.4")

    def _cmake_new_enough(self, required_version):
        try:
            import re
            from io import StringIO
            output = StringIO()
            self.run("cmake --version", output)
            m = re.search(r'cmake version (\d+\.\d+\.\d+)', output.getvalue())
            return Version(m.group(1)) >= required_version
        except:
            return False

    def build_requirements(self):
        if Version(self.version) >= "2.4.1" and not self._cmake_new_enough("3.16.3"):
            self.tool_requires("cmake/3.25.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["BLOSC_IS_SUBPROJECT"] = False
        tc.cache_variables["BLOSC_INSTALL"] = True
        tc.cache_variables["BUILD_STATIC"] = not bool(self.options.shared)
        tc.cache_variables["BUILD_SHARED"] = bool(self.options.shared)
        tc.cache_variables["BUILD_TESTS"] = False
        tc.cache_variables["BUILD_FUZZERS"] = False
        tc.cache_variables["BUILD_BENCHMARKS"] = False
        tc.cache_variables["BUILD_EXAMPLES"] = False
        simd_intrinsics = self.options.get_safe("simd_intrinsics", False)
        tc.cache_variables["DEACTIVATE_AVX2"] = simd_intrinsics != "avx2"
        tc.cache_variables["DEACTIVATE_LZ4"] = not bool(self.options.with_lz4)
        tc.cache_variables["PREFER_EXTERNAL_LZ4"] = True
        tc.cache_variables["DEACTIVATE_ZLIB"] = self.options.with_zlib is None
        tc.cache_variables["PREFER_EXTERNAL_ZLIB"] = True
        tc.cache_variables["DEACTIVATE_ZSTD"] = not bool(self.options.with_zstd)
        tc.cache_variables["PREFER_EXTERNAL_ZSTD"] = True
        tc.cache_variables["BUILD_PLUGINS"] = bool(self.options.with_plugins)
        if self.options.with_zlib == "zlib-ng-compat":
            tc.preprocessor_definitions["ZLIB_COMPAT"] = "1"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        for filename in glob.glob(os.path.join(self.source_folder, "cmake", "Find*.cmake")):
            if os.path.basename(filename) not in [
                "FindSIMD.cmake",
            ]:
                rm(self, os.path.basename(filename), os.path.join(self.source_folder, "cmake"))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        licenses = ["BLOSC.txt", "BITSHUFFLE.txt", "FASTLZ.txt", "LZ4.txt", "ZLIB.txt", "STDINT.txt"]
        for license_file in licenses:
            copy(self, pattern=license_file, dst=os.path.join(self.package_folder, "licenses"), src=os.path.join(self.source_folder, "LICENSES"))

        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # Remove MS runtime files
        for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
            rm(self, pattern=dll_pattern_to_remove, folder=os.path.join(self.package_folder, "bin"), recursive=True)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "blosc2")

        prefix = "lib" if is_msvc(self) and not self.options.shared else ""
        self.cpp_info.libs = [f"{prefix}blosc2"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["rt", "m", "pthread"]
