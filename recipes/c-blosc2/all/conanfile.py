from conans import ConanFile, CMake, tools
from conan.tools.microsoft import is_msvc
import os
import functools
import glob

required_conan_version = ">=1.45.0"

class CBlosc2Conan(ConanFile):
    name = "c-blosc2"
    description = "A fast, compressed, persistent binary data store library for C."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Blosc/c-blosc2"
    topics = ("c-blosc", "blosc", "compression")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "simd_intrinsics": [None, "sse2", "avx2"],
        "with_lz4": [True, False],
        "with_zlib": [None, "zlib", "zlib-ng"],
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
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.simd_intrinsics

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        # c-blosc2 uses zlib-ng with zlib compat options.
        if self.options.with_zlib == "zlib-ng":
            self.options["zlib-ng"].zlib_compat = True

    def requirements(self):
        if self.options.with_lz4:
            self.requires("lz4/1.9.3")
        if self.options.with_zlib == "zlib-ng":
            self.requires("zlib-ng/2.0.6")
        elif self.options.with_zlib == "zlib":
            self.requires("zlib/1.2.12")
        if self.options.with_zstd:
            self.requires("zstd/1.5.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BLOSC_IS_SUBPROJECT"] = False
        cmake.definitions["BLOSC_INSTALL"] = True
        cmake.definitions["BUILD_STATIC"] = not self.options.shared
        cmake.definitions["BUILD_SHARED"] = self.options.shared
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["BUILD_FUZZERS"] = False
        cmake.definitions["BUILD_BENCHMARKS"] = False
        cmake.definitions["BUILD_EXAMPLES"] = False
        simd_intrinsics = self.options.get_safe("simd_intrinsics", False)
        cmake.definitions["DEACTIVATE_AVX2"] = simd_intrinsics != "avx2"
        cmake.definitions["DEACTIVATE_LZ4"] = not self.options.with_lz4
        cmake.definitions["PREFER_EXTERNAL_LZ4"] = self.options.with_lz4
        cmake.definitions["DEACTIVATE_ZLIB"] = self.options.with_zlib == None
        cmake.definitions["PREFER_EXTERNAL_ZLIB"] = self.options.with_zlib != None
        cmake.definitions["DEACTIVATE_ZSTD"] = not self.options.with_zstd
        cmake.definitions["PREFER_EXTERNAL_ZSTD"] = self.options.with_zstd
        cmake.definitions["BUILD_PLUGINS"] = self.options.with_plugins
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        for filename in glob.glob(os.path.join(self._source_subfolder, "cmake", "Find*.cmake")):
            if os.path.basename(filename) not in [
                "FindSIMD.cmake",
            ]:
                os.remove(filename)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        licenses = ["BLOSC.txt", "BITSHUFFLE.txt", "FASTLZ.txt", "LZ4.txt", "ZLIB.txt", "STDINT.txt"]
        for license_file in licenses:
            self.copy(license_file, dst="licenses", src=os.path.join(self._source_subfolder, "LICENSES"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        # Remove MS runtime files
        for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), dll_pattern_to_remove)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "blosc2")
        prefix = "lib" if is_msvc(self) and not self.options.shared else ""
        self.cpp_info.libs = ["{}blosc2".format(prefix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["rt", "m", "pthread"]

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "blosc2"
