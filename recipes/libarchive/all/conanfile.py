from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.32.0"


class LibarchiveConan(ConanFile):
    name = "libarchive"
    description = "Multi-format archive and compression library"
    topics = ("conan", "libarchive", "tar", "data-compressor", "file-compression")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libarchive.org"
    license = "BSD-2-Clause"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_acl": [True, False],
        "with_zlib": [True, False],
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
        "shared": False,
        "fPIC": True,
        "with_acl": True,
        "with_zlib": True,
        "with_bzip2": False,
        "with_libxml2": False,
        "with_expat": False,
        "with_iconv": True,
        "with_pcreposix": False,
        "with_cng": False,
        "with_nettle": False,
        "with_openssl": False,
        "with_libb2": False,
        "with_lz4": False,
        "with_lzo": False,
        "with_lzma": False,
        "with_zstd": False
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
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.with_libxml2:
            self.requires("libxml2/2.9.10")
        if self.options.with_expat:
            self.requires("expat/2.2.10")
        if self.options.with_iconv:
            self.requires("libiconv/1.16")
        if self.options.with_pcreposix:
            self.requires("pcre/8.44")
        if self.options.with_cng:
            # TODO: add cng when available in CCI
            raise ConanInvalidConfiguration("cng recipe not yet available in CCI.")
        if self.options.with_nettle:
            self.requires("nettle/3.6")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1j")
        if self.options.with_libb2:
            self.requires("libb2/20190723")
        if self.options.with_lz4:
            self.requires("lz4/1.9.3")
        if self.options.with_lzo:
            self.requires("lzo/2.10")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.with_zstd:
            self.requires("zstd/1.4.9")

    def validate(self):
        if self.options.with_expat and self.options.with_libxml2:
            raise ConanInvalidConfiguration("libxml2 and expat options are exclusive. They cannot be used together as XML engine")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        # turn off deps to avoid picking up them accidentally
        self._cmake.definitions["ENABLE_NETTLE"] = self.options.with_nettle
        self._cmake.definitions["ENABLE_OPENSSL"] = self.options.with_openssl
        self._cmake.definitions["ENABLE_LIBB2"] = self.options.with_libb2
        self._cmake.definitions["ENABLE_LZ4"] = self.options.with_lz4
        self._cmake.definitions["ENABLE_LZO"] = self.options.with_lzo
        self._cmake.definitions["ENABLE_LZMA"] = self.options.with_lzma
        self._cmake.definitions["ENABLE_ZSTD"] = self.options.with_zstd
        self._cmake.definitions["ENABLE_ZLIB"] = self.options.with_zlib
        self._cmake.definitions["ENABLE_BZip2"] = self.options.with_bzip2
        # requires LibXml2 cmake name
        self._cmake.definitions["ENABLE_LIBXML2"] = self.options.with_libxml2
        self._cmake.definitions["ENABLE_ICONV"] = self.options.with_iconv
        self._cmake.definitions["ENABLE_EXPAT"] = self.options.with_expat
        self._cmake.definitions["ENABLE_PCREPOSIX"] = self.options.with_pcreposix
        if self.options.with_pcreposix:
            self._cmake.definitions["POSIX_REGEX_LIB"] = "LIBPCREPOSIX"
        self._cmake.definitions["ENABLE_LibGCC"] = False
        self._cmake.definitions["ENABLE_CNG"] = self.options.with_cng
        # turn off features
        self._cmake.definitions["ENABLE_ACL"] = self.options.with_acl
        # turn off components
        self._cmake.definitions["ENABLE_TAR"] = False
        self._cmake.definitions["ENABLE_CPIO"] = False
        self._cmake.definitions["ENABLE_CAT"] = False
        self._cmake.definitions["ENABLE_TEST"] = False
        # too strict check
        self._cmake.definitions["ENABLE_WERROR"] = False

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmakelists_path = os.path.join(self._source_subfolder, "CMakeLists.txt")

        # it can possibly override CMAKE_MODULE_PATH provided by generator
        tools.replace_in_file(cmakelists_path,
                              "SET(CMAKE_MODULE_PATH",
                              "LIST(APPEND CMAKE_MODULE_PATH")
        # workaround due to case sensitivity and limitations in cmake_find_package
        # see https://github.com/conan-io/conan/issues/7691
        if self.options.with_bzip2:
            tools.replace_in_file(cmakelists_path, "BZIP2_FOUND", "BZip2_FOUND")
            tools.replace_in_file(cmakelists_path, "BZIP2_INCLUDE_DIR", "BZip2_INCLUDE_DIR")
            tools.replace_in_file(cmakelists_path, "BZIP2_LIBRARIES", "BZip2_LIBRARIES")
        if self.options.with_openssl:
            tools.replace_in_file(cmakelists_path,
                                  "IF(ENABLE_OPENSSL AND NOT CMAKE_SYSTEM_NAME MATCHES \"Darwin\")",
                                  "IF(ENABLE_OPENSSL)")
        if self.options.with_lzma:
            tools.replace_in_file(cmakelists_path, "LIBLZMA_FOUND", "LibLZMA_FOUND")
            tools.replace_in_file(cmakelists_path, "LIBLZMA_INCLUDE_DIR", "LibLZMA_INCLUDE_DIR")
            tools.replace_in_file(cmakelists_path, "LIBLZMA_LIBRARIES", "LibLZMA_LIBRARIES")
        # add possible names for lz4 library
        if not self.options.shared:
            tools.replace_in_file(cmakelists_path,
                                  "FIND_LIBRARY(LZ4_LIBRARY NAMES lz4 liblz4)",
                                  "FIND_LIBRARY(LZ4_LIBRARY NAMES lz4 liblz4 lz4_static liblz4_static)")

        # Exclude static/shared targets from build
        if self.options.shared:
            tools.save(os.path.join(self._source_subfolder, "libarchive", "CMakeLists.txt"),
                       "set_target_properties(archive_static PROPERTIES EXCLUDE_FROM_ALL 1 EXCLUDE_FROM_DEFAULT_BUILD 1)",
                       append=True)
        else:
            tools.save(os.path.join(self._source_subfolder, "libarchive", "CMakeLists.txt"),
                       "set_target_properties(archive PROPERTIES EXCLUDE_FROM_ALL 1 EXCLUDE_FROM_DEFAULT_BUILD 1)",
                       append=True)

        # Exclude static/shared targets from install
        if self.options.shared:
            tools.replace_in_file(os.path.join(self._source_subfolder, "libarchive", "CMakeLists.txt"),
                                  "INSTALL(TARGETS archive archive_static",
                                  "INSTALL(TARGETS archive")
        else:
            tools.replace_in_file(os.path.join(self._source_subfolder, "libarchive", "CMakeLists.txt"),
                                  "INSTALL(TARGETS archive archive_static",
                                  "INSTALL(TARGETS archive_static")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "LibArchive"
        self.cpp_info.names["cmake_find_package_multi"] = "LibArchive"
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            self.cpp_info.defines = ["LIBARCHIVE_STATIC"]
