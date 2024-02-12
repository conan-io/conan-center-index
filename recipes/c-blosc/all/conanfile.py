from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class CbloscConan(ConanFile):
    name = "c-blosc"
    description = "An extremely fast, multi-threaded, meta-compressor library."
    license = "BSD-3-Clause"
    topics = ("blosc", "compression")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Blosc/c-blosc"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "simd_intrinsics": [None, "sse2", "avx2"],
        "with_lz4": [True, False],
        "with_snappy": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "simd_intrinsics": "sse2",
        "with_lz4": True,
        "with_snappy": True,
        "with_zlib": True,
        "with_zstd": True,
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
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_lz4:
            self.requires("lz4/1.9.4")
        if self.options.with_snappy:
            self.requires("snappy/1.1.10")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BLOSC_INSTALL"] = True
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.variables["BUILD_SHARED"] = self.options.shared
        tc.variables["BUILD_TESTS"] = False
        if Version(self.version) >= "1.20.0":
            tc.variables["BUILD_FUZZERS"] = False
        tc.variables["BUILD_BENCHMARKS"] = False
        simd_intrinsics = self.options.get_safe("simd_intrinsics", False)
        tc.variables["DEACTIVATE_SSE2"] = simd_intrinsics not in ["sse2", "avx2"]
        tc.variables["DEACTIVATE_AVX2"] = simd_intrinsics != "avx2"
        tc.variables["DEACTIVATE_LZ4"] = not self.options.with_lz4
        tc.variables["DEACTIVATE_SNAPPY"] = not self.options.with_snappy
        tc.variables["DEACTIVATE_ZLIB"] = not self.options.with_zlib
        tc.variables["DEACTIVATE_ZSTD"] = not self.options.with_zstd
        tc.variables["DEACTIVATE_SYMBOLS_CHECK"] = True
        tc.variables["PREFER_EXTERNAL_LZ4"] = True
        if Version(self.version) < "1.19.0":
            tc.variables["PREFER_EXTERNAL_SNAPPY"] = True
        tc.variables["PREFER_EXTERNAL_ZLIB"] = True
        tc.variables["PREFER_EXTERNAL_ZSTD"] = True
        tc.variables["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = True
        # Generate a relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        rmdir(self, os.path.join(self.source_folder, "cmake"))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        licenses = ["BLOSC.txt", "BITSHUFFLE.txt", "FASTLZ.txt"]
        for license_file in licenses:
            copy(self, license_file, src=os.path.join(self.source_folder, "LICENSES"), dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "blosc")
        prefix = "lib" if is_msvc(self) and not self.options.shared else ""
        self.cpp_info.libs = [f"{prefix}blosc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
