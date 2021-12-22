import os
from conans import ConanFile, tools, CMake


class MinizipNgConan(ConanFile):
    name = "minizip-ng"
    description = "Fork of the popular zip manipulation library found in the zlib distribution."
    topics = ("conan", "compression", "zip")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zlib-ng/minizip-ng"
    license = "Zlib"
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package", "pkg_config"
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
        if not tools.is_apple_os(self.settings.os):
            del self.options.with_libcomp

    def build_requirements(self):
        self.build_requires('pkgconf/1.7.3')

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.options.mz_compatibility:
            self.provides = "minizip"
        if self.options.get_safe("with_libcomp"):
            del self.options.with_zlib

    def requirements(self):
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/1.2.11")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.with_zstd:
            self.requires("zstd/1.5.0")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1l")
        if self.settings.os != "Windows":
            if self.options.get_safe("with_iconv"):
                self.requires("libiconv/1.16")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["MZ_FETCH_LIBS"] = False
        self._cmake.definitions["MZ_COMPAT"] = self.options.mz_compatibility
        self._cmake.definitions["MZ_ZLIB"] = self.options.get_safe("with_zlib", False)
        self._cmake.definitions["MZ_BZIP2"] = self.options.with_bzip2
        self._cmake.definitions["MZ_LZMA"] = self.options.with_lzma
        self._cmake.definitions["MZ_ZSTD"] = self.options.with_zstd
        self._cmake.definitions["MZ_OPENSSL"] = self.options.with_openssl
        self._cmake.definitions["MZ_LIBCOMP"] = self.options.get_safe("with_libcomp", False)

        if self.settings.os != "Windows":
            self._cmake.definitions["MZ_ICONV"] = self.options.with_iconv
            self._cmake.definitions["MZ_LIBBSD"] = self.options.with_libbsd

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set_target_properties(${PROJECT_NAME} PROPERTIES POSITION_INDEPENDENT_CODE 1)",
                              "")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "minizip"
        self.cpp_info.filenames["cmake_find_package_multi"] = "minizip"
        self.cpp_info.names["cmake_find_package"] = "MINIZIP"
        self.cpp_info.names["cmake_find_package_multi"] = "MINIZIP"
        self.cpp_info.names["pkg_config"] = "minizip"
        self.cpp_info.components["minizip"].names["cmake_find_package"] = "minizip"
        self.cpp_info.components["minizip"].names["cmake_find_package_multi"] = "minizip"
        self.cpp_info.components["minizip"].libs = tools.collect_libs(self)

        if self.options.get_safe("with_zlib"):
            self.cpp_info.components["minizip"].requires.append("zlib::zlib")
        if self.options.with_bzip2:
            self.cpp_info.components["minizip"].requires.append("bzip2::bzip2")
        if self.options.with_lzma:
            self.cpp_info.components["minizip"].requires.append("xz_utils::xz_utils")
        if self.options.with_zstd:
            self.cpp_info.components["minizip"].requires.append("zstd::zstd")
        if self.options.with_openssl:
            self.cpp_info.components["minizip"].requires.append("openssl::openssl")
        if self.settings.os != "Windows" and self.options.with_iconv:
            self.cpp_info.components["minizip"].requires.append("libiconv::libiconv")

        if self.options.with_lzma:
            self.cpp_info.components["minizip"].defines.append('HAVE_LZMA')
        if tools.is_apple_os(self.settings.os) and self.options.get_safe("with_libcomp"):
            self.cpp_info.components["minizip"].defines.append('HAVE_LIBCOMP')
        if self.options.with_bzip2:
            self.cpp_info.components["minizip"].defines.append('HAVE_BZIP2')
