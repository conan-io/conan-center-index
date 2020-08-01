from conans import ConanFile, CMake, tools
import os


class MinizipConan(ConanFile):
    name = "minizip"
    description = "minizip is a zip manipulation library written in C that is supported on Windows, macOS, and Linux."
    topics = ("conan", "minizip", "compression")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nmoinvaz/minizip"
    license = "Zlib"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake_find_package"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False],
        "compat": [True, False],
        "zlib": [True, False],
        "bzip2": [True, False],
        "zstd": [True, False],
        "lzma": [True, False],
        "pkcrypt": [True, False],
        "wzaes": [True, False],
        "libcomp": [True, False],
        "openssl": [True, False],
        "libbsd": [True, False],
        "brg": [True, False],
        "signing": [True, False],
        "compress_only": [True, False],
        "decompress_only": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "compat": True,
        "zlib": True,
        "bzip2": True,
        "lzma": True,
        "zstd": True,
        "pkcrypt": True,
        "wzaes": True,
        "libcomp": False,
        "openssl": False,
        "libbsd": True,
        "brg": False,
        "signing": True,
        "compress_only": False,
        "decompress_only": False
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    requires = (
    )
    
    def requirements(self):
        if self.options.zlib:
            self.requires("zlib/1.2.11")
        if self.options.bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.zstd:
            self.requires("zstd/1.4.5")
        if self.options.openssl:
            self.requires("openssl/1.1.1g")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        
    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["MZ_COMPAT"] = self.options.compat
            self._cmake.definitions["MZ_ZLIB"] = self.options.zlib
            self._cmake.definitions["MZ_BZIP2"] = self.options.bzip2
            self._cmake.definitions["MZ_LZMA"] = self.options.lzma
            self._cmake.definitions["MZ_ZSTD"] = self.options.zstd
            self._cmake.definitions["MZ_PKCRYPT"] = self.options.pkcrypt
            self._cmake.definitions["MZ_WZAES"] = self.options.wzaes
            self._cmake.definitions["MZ_LIBCOMP"] = self.options.libcomp
            self._cmake.definitions["MZ_OPENSSL"] = self.options.openssl
            self._cmake.definitions["MZ_LIBBSD"] = self.options.libbsd
            self._cmake.definitions["MZ_BRG"] = self.options.brg
            self._cmake.definitions["MZ_SIGNING"] = self.options.signing
            self._cmake.definitions["MZ_COMPRESS_ONLY"] = self.options.compress_only
            self._cmake.definitions["MZ_DECOMPRESS_ONLY"] = self.options.decompress_only
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
