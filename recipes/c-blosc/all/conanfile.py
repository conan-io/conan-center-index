import os

from conans import ConanFile, CMake, tools

class CbloscConan(ConanFile):
    name = "c-blosc"
    description = "An extremely fast, multi-threaded, meta-compressor library."
    license = "BSD-3-Clause"
    topics = ("conan", "c-blosc", "blosc", "compression")
    homepage = "https://github.com/Blosc/c-blosc"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_lz4": [True, False],
        "with_snappy": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_lz4": True,
        "with_snappy": True,
        "with_zlib": True,
        "with_zstd": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.with_lz4:
            self.requires("lz4/1.9.2")
        if self.options.with_snappy:
            self.requires("snappy/1.1.8")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_zstd:
            self.requires("zstd/1.4.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BLOSC_INSTALL"] = True
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_BENCHMARKS"] = False
        self._cmake.definitions["DEACTIVATE_SSE2"] = False
        self._cmake.definitions["DEACTIVATE_AVX2"] = False
        self._cmake.definitions["DEACTIVATE_LZ4"] = not self.options.with_lz4
        self._cmake.definitions["DEACTIVATE_SNAPPY"] = not self.options.with_snappy
        self._cmake.definitions["DEACTIVATE_ZLIB"] = not self.options.with_zlib
        self._cmake.definitions["DEACTIVATE_ZSTD"] = not self.options.with_zstd
        self._cmake.definitions["DEACTIVATE_SYMBOLS_CHECK"] = True
        self._cmake.definitions["PREFER_EXTERNAL_LZ4"] = True
        self._cmake.definitions["PREFER_EXTERNAL_SNAPPY"] = True
        self._cmake.definitions["PREFER_EXTERNAL_ZLIB"] = True
        self._cmake.definitions["PREFER_EXTERNAL_ZSTD"] = True
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
        self.cpp_info.names["pkg_config"] = "blosc"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
