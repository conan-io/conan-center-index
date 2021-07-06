from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibZipConan(ConanFile):
    name = "libzip"
    description = "A C library for reading, creating, and modifying zip archives"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nih-at/libzip"
    license = "BSD-3-Clause"
    topics = ("conan", "zip", "libzip", "zip-archives", "zip-editing")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_bzip2": [True, False],
        "with_lzma": [True, False],
        "with_zstd": [True, False],
        "crypto": [False, "win32", "openssl", "mbedtls", "auto"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_bzip2": True,
        "with_lzma": True,
        "with_zstd": True,
        "crypto": "auto"
    }
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _crypto(self):
        if self.options.crypto == "auto":
            return "win32" if self.settings.os == "Windows" else "openssl"
        return self.options.crypto

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self._crypto == "win32" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Windows is required to use win32 crypto libraries")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.11")

        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")

        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")

        if self.options.with_zstd:
            self.requires("zstd/1.4.9")

        if self._crypto == "openssl":
            self.requires("openssl/1.1.1k")
        elif self._crypto == "mbedtls":
            self.requires("mbedtls/2.25")

    def package_id(self):
        self.info.options.crypto = self._crypto

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_REGRESS"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_DOC"] = False

        self._cmake.definitions["ENABLE_LZMA"] = self.options.with_lzma
        self._cmake.definitions["ENABLE_BZIP2"] = self.options.with_bzip2
        self._cmake.definitions["ENABLE_ZSTD"] = self.options.with_zstd

        self._cmake.definitions["ENABLE_COMMONCRYPTO"] = False  # TODO: We need CommonCrypto package
        self._cmake.definitions["ENABLE_GNUTLS"] = False  # TODO: We need GnuTLS package

        self._cmake.definitions["ENABLE_MBEDTLS"] = self._crypto == "mbedtls"
        self._cmake.definitions["ENABLE_OPENSSL"] = self._crypto == "openssl"
        self._cmake.definitions["ENABLE_WINDOWS_CRYPTO"] = self._crypto == "win32"

        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "libzip"
        self.cpp_info.names["cmake_find_package_multi"] = "libzip"
        self.cpp_info.names["pkg_config"] = "libzip"
        self.cpp_info.components["_libzip"].names["cmake_find_package"] = "zip"
        self.cpp_info.components["_libzip"].names["cmake_find_package_multi"] = "zip"
        self.cpp_info.components["_libzip"].names["pkg_config"] = "libzip"
        self.cpp_info.components["_libzip"].libs = ["zip"]
        if self.settings.os == "Windows":
            self.cpp_info.components["_libzip"].system_libs = ["advapi32"]
            if self._crypto == "win32":
                self.cpp_info.components["_libzip"].system_libs.append("bcrypt")
        self.cpp_info.components["_libzip"].requires = ["zlib::zlib"]
        if self.options.with_bzip2:
            self.cpp_info.components["_libzip"].requires.append("bzip2::bzip2")
        if self.options.with_lzma:
            self.cpp_info.components["_libzip"].requires.append("xz_utils::xz_utils")
        if self.options.with_zstd:
            self.cpp_info.components["_libzip"].requires.append("zstd::zstd")
        if self._crypto == "openssl":
            self.cpp_info.components["_libzip"].requires.append("openssl::openssl")
        elif self._crypto == "mbedtls":
            self.cpp_info.components["_libzip"].requires.append("mbedtls::mbedtls")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
