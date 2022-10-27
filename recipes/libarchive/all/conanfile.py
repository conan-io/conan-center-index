from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.layout import cmake_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.52.0"


class LibarchiveConan(ConanFile):
    name = "libarchive"
    description = "Multi-format archive and compression library"
    topics = "tar", "data-compressor", "file-compression"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libarchive.org"
    license = "BSD-2-Clause"
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
        "with_zstd": [True, False],
        "with_mbedtls": [True, False],
        "with_xattr": [True, False],
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
        "with_zstd": False,
        "with_mbedtls": False,
        "with_xattr": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "3.4.2":
            del self.options.with_mbedtls

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.with_libxml2:
            self.requires("libxml2/2.9.14")
        if self.options.with_expat:
            self.requires("expat/2.4.9")
        if self.options.with_iconv:
            self.requires("libiconv/1.17")
        if self.options.with_pcreposix:
            self.requires("pcre/8.45")
        if self.options.with_nettle:
            self.requires("nettle/3.8.1")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")
        if self.options.with_libb2:
            self.requires("libb2/20190723")
        if self.options.with_lz4:
            self.requires("lz4/1.9.4")
        if self.options.with_lzo:
            self.requires("lzo/2.10")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.with_zstd:
            self.requires("zstd/1.5.2")
        if self.options.get_safe("with_mbedtls"):
            self.requires("mbedtls/3.2.1")

    def validate(self):
        if self.info.settings.os != "Windows" and self.info.options.with_cng:
            # TODO: add cng when available in CCI
            raise ConanInvalidConfiguration("cng recipe not yet available in CCI.")
        if self.info.options.with_expat and self.info.options.with_libxml2:
            raise ConanInvalidConfiguration("libxml2 and expat options are exclusive. They cannot be used together as XML engine")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()
        tc = CMakeToolchain(self)
        # turn off deps to avoid picking up them accidentally
        tc.variables["ENABLE_NETTLE"] = self.options.with_nettle
        tc.variables["ENABLE_OPENSSL"] = self.options.with_openssl
        tc.variables["ENABLE_LIBB2"] = self.options.with_libb2
        tc.variables["ENABLE_LZ4"] = self.options.with_lz4
        tc.variables["ENABLE_LZO"] = self.options.with_lzo
        tc.variables["ENABLE_LZMA"] = self.options.with_lzma
        tc.variables["ENABLE_ZSTD"] = self.options.with_zstd
        tc.variables["ENABLE_ZLIB"] = self.options.with_zlib
        tc.variables["ENABLE_BZip2"] = self.options.with_bzip2
        # requires LibXml2 cmake name
        tc.variables["ENABLE_LIBXML2"] = self.options.with_libxml2
        tc.variables["ENABLE_ICONV"] = self.options.with_iconv
        tc.variables["ENABLE_EXPAT"] = self.options.with_expat
        tc.variables["ENABLE_PCREPOSIX"] = self.options.with_pcreposix
        if self.options.with_pcreposix:
            tc.variables["POSIX_REGEX_LIB"] = "LIBPCREPOSIX"
        tc.variables["ENABLE_LibGCC"] = False
        tc.variables["ENABLE_CNG"] = self.options.with_cng
        # turn off features
        tc.variables["ENABLE_ACL"] = self.options.with_acl
        # turn off components
        tc.variables["ENABLE_TAR"] = False
        tc.variables["ENABLE_CPIO"] = False
        tc.variables["ENABLE_CAT"] = False
        tc.variables["ENABLE_TEST"] = False
        # too strict check
        tc.variables["ENABLE_WERROR"] = False
        if Version(self.version) >= "3.4.2":
            tc.variables["ENABLE_MBEDTLS"] = self.options.with_mbedtls
        tc.variables["ENABLE_XATTR"] = self.options.with_xattr

        if self.settings.os == "Windows" and self.settings.get_safe("os.subsystem") != "cygwin":
            tc.cache_variables["ZLIB_WINAPI"] = "yes"

        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        cmakelists_path = os.path.join(self.source_folder, "CMakeLists.txt")

        replace_in_file(self, cmakelists_path,
                        "CMAKE_MINIMUM_REQUIRED(VERSION 2.8.12 FATAL_ERROR)",
                        "CMAKE_MINIMUM_REQUIRED(VERSION 3.1)")

        # it can possibly override CMAKE_MODULE_PATH provided by generator
        replace_in_file(self, cmakelists_path,
                        "SET(CMAKE_MODULE_PATH",
                        "LIST(APPEND CMAKE_MODULE_PATH")
        # allow openssl on macOS
        if self.options.with_openssl:
            replace_in_file(self, cmakelists_path,
                            "IF(ENABLE_OPENSSL AND NOT CMAKE_SYSTEM_NAME MATCHES \"Darwin\")",
                            "IF(ENABLE_OPENSSL)")
        # wrong lzma cmake var name
        if self.options.with_lzma:
            replace_in_file(self, cmakelists_path, "LIBLZMA_INCLUDE_DIR", "LIBLZMA_INCLUDE_DIRS")
        # add possible names for lz4 library
        if not self.options.shared:
            replace_in_file(self, cmakelists_path,
                            "FIND_LIBRARY(LZ4_LIBRARY NAMES lz4 liblz4)",
                            "FIND_LIBRARY(LZ4_LIBRARY NAMES lz4 liblz4 lz4_static liblz4_static)")

        # Exclude static/shared targets from build
        if self.options.shared:
            save(self, os.path.join(self.source_folder, "libarchive", "CMakeLists.txt"),
                "set_target_properties(archive_static PROPERTIES EXCLUDE_FROM_ALL 1 EXCLUDE_FROM_DEFAULT_BUILD 1)",
                append=True)
        else:
            save(self, os.path.join(self.source_folder, "libarchive", "CMakeLists.txt"),
                "set_target_properties(archive PROPERTIES EXCLUDE_FROM_ALL 1 EXCLUDE_FROM_DEFAULT_BUILD 1)",
                append=True)

        # Exclude static/shared targets from install
        if self.options.shared:
            replace_in_file(self, os.path.join(self.source_folder, "libarchive", "CMakeLists.txt"),
                            "INSTALL(TARGETS archive archive_static",
                            "INSTALL(TARGETS archive")
        else:
            replace_in_file(self, os.path.join(self.source_folder, "libarchive", "CMakeLists.txt"),
                            "INSTALL(TARGETS archive archive_static",
                            "INSTALL(TARGETS archive_static")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "LibArchive")
        self.cpp_info.set_property("cmake_target_name", "LibArchive::LibArchive")
        self.cpp_info.set_property("pkg_config_name", "libarchive")

        self.cpp_info.names["cmake_find_package"] = "LibArchive"
        self.cpp_info.names["cmake_find_package_multi"] = "LibArchive"

        self.cpp_info.libs = collect_libs(self)
        if self.settings.os == "Windows" and self.options.with_cng:
            self.cpp_info.system_libs.append("bcrypt")
        if is_msvc(self) and not self.options.shared:
            self.cpp_info.defines = ["LIBARCHIVE_STATIC"]
