from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os


class MinizipNgConan(ConanFile):
    name = "minizip-ng"
    description = "Fork of the popular zip manipulation library found in the zlib distribution."
    topics = ("conan", "compression", "zip")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zlib-ng/minizip-ng"
    license = "BSD-3-Clause"
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "mz_compatibility": [True, False],
        "with_zlib": [True, False],
        "with_bzip2": [True, False],
        "with_lzma": [True, False],
        "with_zstd": [True, False],
        "with_openssl": [True, False],
        "with_iconv": [True, False],
        "with_libbsd": [True, False],
        "with_libcomp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "mz_compatibility": False,
        "with_zlib": True,
        "with_bzip2": True,
        "with_lzma": True,
        "with_zstd": True,
        "with_openssl": True,
        "with_iconv": True,
        "with_libbsd": True,
        "with_libcomp": True,
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
            del self.options.with_iconv
            del self.options.with_libbsd

    def build_requirements(self):
        self.build_requires('pkgconf/1.7.3')

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.with_zstd:
            self.requires("zstd/1.4.8")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1i")
        if self.settings.os != "Windows":
            if self.options.with_iconv:
                self.requires("libiconv/1.16")
            if self.options.with_libbsd:
                self.requires("libbsd/0.10.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "minizip-ng-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["MZ_FETCH_LIBS"] = False
        self._cmake.definitions["MZ_COMPAT"] = self.options.mz_compatibility
        self._cmake.definitions["MZ_ZLIB"] = self.options.with_zlib
        self._cmake.definitions["MZ_BZIP2"] = self.options.with_bzip2
        self._cmake.definitions["MZ_LZMA"] = self.options.with_lzma
        self._cmake.definitions["MZ_ZSTD"] = self.options.with_zstd
        self._cmake.definitions["MZ_OPENSSL"] = self.options.with_openssl
        self._cmake.definitions["MZ_LIBCOMP"] = tools.is_apple_os(self.settings.os) and self.options.with_libcomp

        if self.settings.os != "Windows":
            self._cmake.definitions["MZ_ICONV"] = self.options.with_iconv

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "minizip"
        self.cpp_info.names["cmake_find_package_multi"] = "minizip"
        self.cpp_info.names["pkg_config"] = "minizip"
        self.cpp_info.libs = tools.collect_libs(self)
