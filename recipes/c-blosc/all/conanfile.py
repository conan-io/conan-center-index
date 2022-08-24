from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.36.0"


class CbloscConan(ConanFile):
    name = "c-blosc"
    description = "An extremely fast, multi-threaded, meta-compressor library."
    license = "BSD-3-Clause"
    topics = ("c-blosc", "blosc", "compression")
    homepage = "https://github.com/Blosc/c-blosc"
    url = "https://github.com/conan-io/conan-center-index"

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

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

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

    def requirements(self):
        if self.options.with_lz4:
            self.requires("lz4/1.9.3")
        if self.options.with_snappy:
            self.requires("snappy/1.1.9")
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.with_zstd:
            self.requires("zstd/1.5.2")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # Remove folder containing custom FindLib.cmake files
        tools.rmdir(os.path.join(self._source_subfolder, "cmake"))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BLOSC_INSTALL"] = True
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["BUILD_TESTS"] = False
        if tools.Version(self.version) >= "1.20.0":
            self._cmake.definitions["BUILD_FUZZERS"] = False
        self._cmake.definitions["BUILD_BENCHMARKS"] = False
        simd_intrinsics = self.options.get_safe("simd_intrinsics", False)
        self._cmake.definitions["DEACTIVATE_SSE2"] = simd_intrinsics not in ["sse2", "avx2"]
        self._cmake.definitions["DEACTIVATE_AVX2"] = simd_intrinsics != "avx2"
        self._cmake.definitions["DEACTIVATE_LZ4"] = not self.options.with_lz4
        self._cmake.definitions["DEACTIVATE_SNAPPY"] = not self.options.with_snappy
        self._cmake.definitions["DEACTIVATE_ZLIB"] = not self.options.with_zlib
        self._cmake.definitions["DEACTIVATE_ZSTD"] = not self.options.with_zstd
        self._cmake.definitions["DEACTIVATE_SYMBOLS_CHECK"] = True
        self._cmake.definitions["PREFER_EXTERNAL_LZ4"] = True
        if tools.Version(self.version) < "1.19.0":
            self._cmake.definitions["PREFER_EXTERNAL_SNAPPY"] = True
        self._cmake.definitions["PREFER_EXTERNAL_ZLIB"] = True
        self._cmake.definitions["PREFER_EXTERNAL_ZSTD"] = True
        # Generate a relocatable shared lib on Macos
        self._cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        licenses = ["BLOSC.txt", "BITSHUFFLE.txt", "FASTLZ.txt"]
        for license_file in licenses:
            self.copy(license_file, dst="licenses", src=os.path.join(self._source_subfolder, "LICENSES"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "blosc")
        prefix = "lib" if self._is_msvc and not self.options.shared else ""
        self.cpp_info.libs = ["{}blosc".format(prefix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "blosc"
