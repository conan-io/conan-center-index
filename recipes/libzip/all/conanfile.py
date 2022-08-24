from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class LibZipConan(ConanFile):
    name = "libzip"
    description = "A C library for reading, creating, and modifying zip archives"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nih-at/libzip"
    license = "BSD-3-Clause"
    topics = ("zip", "libzip", "zip-archives", "zip-editing")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_bzip2": [True, False],
        "with_lzma": [True, False],
        "with_zstd": [True, False],
        "crypto": [False, "win32", "openssl", "mbedtls", "auto"],
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_bzip2": True,
        "with_lzma": True,
        "with_zstd": True,
        "crypto": "openssl",
        "tools": True,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _has_zstd_support(self):
        return tools.scm.Version(self, self.version) >= "1.8.0"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_zstd_support:
            del self.options.zstd
        # Default crypto backend on windows
        if self.settings.os == "Windows":
            self.options.crypto = "win32"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

        # Deprecate "auto" value of crypto option
        if self.options.crypto == "auto":
            crypto_value = "win32" if self.settings.os == "Windows" else "openssl"
            self.output.warn("'auto' value of 'crypto' option is deprecated, fallback to default value on {}: {}".format(self.settings.os, crypto_value))
            self.options.crypto = crypto_value

    def requirements(self):
        self.requires("zlib/1.2.12")

        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")

        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")

        if self.options.get_safe("with_zstd"):
            self.requires("zstd/1.5.2")

        if self.options.crypto == "openssl":
            self.requires("openssl/1.1.1q")
        elif self.options.crypto == "mbedtls":
            self.requires("mbedtls/3.2.1")

    def validate(self):
        if self.options.crypto == "win32" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Windows is required to use win32 crypto libraries")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        top_cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        # Honor zstd enabled
        if self._has_zstd_support:
            lib_cmakelists = os.path.join(self._source_subfolder, "lib", "CMakeLists.txt")
            tools.files.replace_in_file(self, top_cmakelists, "find_package(Zstd)", "find_package(zstd)")
            tools.files.replace_in_file(self, top_cmakelists, "Zstd_FOUND", "zstd_FOUND")
            tools.files.replace_in_file(self, lib_cmakelists, "Zstd::Zstd", "zstd::zstd")
        # Do not pollute rpath of installed binaries
        tools.files.replace_in_file(self, 
            top_cmakelists,
            "set(CMAKE_INSTALL_RPATH ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR})",
            "",
        )
        tools.files.replace_in_file(self, 
            top_cmakelists,
            "set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)",
            "",
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TOOLS"] = self.options.tools
        self._cmake.definitions["BUILD_REGRESS"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_DOC"] = False

        self._cmake.definitions["ENABLE_LZMA"] = self.options.with_lzma
        self._cmake.definitions["ENABLE_BZIP2"] = self.options.with_bzip2
        if self._has_zstd_support:
            self._cmake.definitions["ENABLE_ZSTD"] = self.options.with_zstd

        self._cmake.definitions["ENABLE_COMMONCRYPTO"] = False  # TODO: We need CommonCrypto package
        self._cmake.definitions["ENABLE_GNUTLS"] = False  # TODO: We need GnuTLS package

        self._cmake.definitions["ENABLE_MBEDTLS"] = self.options.crypto == "mbedtls"
        self._cmake.definitions["ENABLE_OPENSSL"] = self.options.crypto == "openssl"
        self._cmake.definitions["ENABLE_WINDOWS_CRYPTO"] = self.options.crypto == "win32"

        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libzip")
        self.cpp_info.set_property("cmake_target_name", "libzip::zip")
        self.cpp_info.set_property("pkg_config_name", "libzip")

        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["_libzip"].libs = ["zip"]
        if self.settings.os == "Windows":
            self.cpp_info.components["_libzip"].system_libs = ["advapi32"]
            if self.options.crypto == "win32":
                self.cpp_info.components["_libzip"].system_libs.append("bcrypt")

        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "libzip"
        self.cpp_info.names["cmake_find_package_multi"] = "libzip"
        self.cpp_info.components["_libzip"].names["cmake_find_package"] = "zip"
        self.cpp_info.components["_libzip"].names["cmake_find_package_multi"] = "zip"
        self.cpp_info.components["_libzip"].set_property("cmake_target_name", "libzip::zip")
        self.cpp_info.components["_libzip"].set_property("pkg_config_name", "libzip")
        self.cpp_info.components["_libzip"].requires = ["zlib::zlib"]
        if self.options.with_bzip2:
            self.cpp_info.components["_libzip"].requires.append("bzip2::bzip2")
        if self.options.with_lzma:
            self.cpp_info.components["_libzip"].requires.append("xz_utils::xz_utils")
        if self.options.get_safe("with_zstd"):
            self.cpp_info.components["_libzip"].requires.append("zstd::zstd")
        if self.options.crypto == "openssl":
            self.cpp_info.components["_libzip"].requires.append("openssl::crypto")
        elif self.options.crypto == "mbedtls":
            self.cpp_info.components["_libzip"].requires.append("mbedtls::mbedtls")
