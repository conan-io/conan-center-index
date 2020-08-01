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
        "zlib/1.2.11",
        "zstd/1.4.5",
        "bzip2/1.0.8",
    )

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
