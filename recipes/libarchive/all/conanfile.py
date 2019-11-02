from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibarchiveConan(ConanFile):
    name = "libarchive"
    description = "C library for encoding, decoding and manipulating JSON data"
    topics = ("conan", "libarchive", "tar", "data-compressor", "file-compression")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libarchive.org"
    license = "https://raw.githubusercontent.com/libarchive/libarchive/master/COPYING"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_acl": [True, False],
        "with_bzip2": [True, False],
        "with_libxml2": [True, False],
        "with_expat": [True, False],
        "with_iconv": [True, False],
        "with_pcreposix": [True, False],
        "with_cng": [True, False],
        "with_nettle": [True, False],
        "with_openssl": [True, False],
        "with_libb2": [True, False],
        "with_lz4": [True, False],
        "with_lzo": [True, False],
        "with_lzma": [True, False],
        "with_zstd": [True, False]
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'with_acl': True,
        'with_bzip2': False,
        'with_libxml2': False,
        'with_expat': False,
        'with_iconv': True,
        'with_pcreposix': False,
        'with_cng': False,
        'with_nettle': False,
        'with_openssl': False,
        'with_libb2': False,
        'with_lz4': False,
        'with_lzo': False,
        'with_lzma': False,
        'with_zstd': False
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.options.with_expat and self.options.with_libxml2:
            raise ConanInvalidConfiguration("Only libxml2 or expat can be used as XML engine")

    def build_requirements(self):
        if tools.os_info.is_windows and os.environ.get("CONAN_BASH_PATH", None) is None:
            self.build_requires("msys2/20161025")

    def requirements(self):
        self.requires.add('zlib/1.2.11')
        if self.options.with_bzip2:
            self.requires.add('bzip2/1.0.8')
        if self.options.with_openssl:
            self.requires.add("openssl/1.1.1d")
        if self.options.with_lz4:
            self.requires.add("lz4/1.9.2")
        if self.options.with_zstd:
            self.requires.add("zstd/1.4.3")
        if self.options.with_libxml2:
            self.requires.add("libxml2/2.9.9")
        if self.options.with_expat:
            self.requires.add("expat/2.2.7")
        if self.options.with_iconv:
            self.requires("libiconv/1.15")
        # deps not covered yet:
        # pcreposix, cng, nettle, libb2, lzma

    def _configure_cmake(self):
        cmake = CMake(self)
        # turn off deps to avoid picking up them accidentally
        cmake.definitions["ENABLE_NETTLE"] = self.options.with_nettle
        cmake.definitions["ENABLE_OPENSSL"] = self.options.with_openssl
        cmake.definitions["ENABLE_LIBB2"] = self.options.with_libb2
        cmake.definitions["ENABLE_LZ4"] = self.options.with_lz4
        cmake.definitions["ENABLE_LZO"] = self.options.with_lzo
        cmake.definitions["ENABLE_LZMA"] = self.options.with_lzma
        cmake.definitions["ENABLE_ZSTD"] = self.options.with_zstd
        cmake.definitions["ENABLE_ZLIB"] = True
        cmake.definitions["ENABLE_BZip2"] = self.options.with_bzip2
        # requires LibXml2 cmake name
        cmake.definitions["ENABLE_LIBXML2"] = self.options.with_libxml2
        cmake.definitions["ENABLE_ICONV"] = self.options.with_iconv
        cmake.definitions["ENABLE_EXPAT"] = self.options.with_expat
        cmake.definitions["ENABLE_PCREPOSIX"] = self.options.with_pcreposix
        cmake.definitions["ENABLE_LibGCC"] = False
        cmake.definitions["ENABLE_CNG"] = self.options.with_cng
        # turn off features
        cmake.definitions["ENABLE_ACL"] = self.options.with_acl
        # turn off components
        cmake.definitions["ENABLE_TAR"] = False
        cmake.definitions["ENABLE_CPIO"] = False
        cmake.definitions["ENABLE_CAT"] = False
        cmake.definitions["ENABLE_TEST"] = False

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        if self.options.shared:
            tools.replace_in_file(os.path.join(self._source_subfolder, "libarchive", "CMakeLists.txt"),
                                  "INSTALL(TARGETS archive archive_static",
                                  "INSTALL(TARGETS archive")
        else:
            tools.replace_in_file(os.path.join(self._source_subfolder, "libarchive", "CMakeLists.txt"),
                                  "INSTALL(TARGETS archive archive_static",
                                  "INSTALL(TARGETS archive_static")

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # drop pc and cmake file
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'share'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
