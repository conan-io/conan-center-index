from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class QpdfConan(ConanFile):
    name = "qpdf"
    description = "QPDF is a command-line tool and C++ library that performs content-preserving transformations on PDF files."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/qpdf/qpdf"
    topics = ("pdf",)
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": ["internal", "openssl", "gnutls"],
        "with_jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": "openssl",
        "with_jpeg": "libjpeg",
    }

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "14",
            "msvc": "190",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # https://qpdf.readthedocs.io/en/stable/installation.html#basic-dependencies
        self.requires("zlib/1.2.13")
        if self.options.with_ssl == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.5")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.options.with_ssl == "gnutls":
            raise ConanInvalidConfiguration("GnuTLS is not available in Conan Center yet.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = VirtualBuildEnv(self)
        tc.generate()
        tc = CMakeToolchain(self)
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        # https://qpdf.readthedocs.io/en/latest/installation.html#build-time-crypto-selection
        tc.variables["USE_IMPLICIT_CRYPTO"] = False
        tc.cache_variables["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = True
        if self.options.with_ssl == "internal":
            tc.variables["REQUIRE_CRYPTO_NATIVE"] = True
            tc.variables["REQUIRE_CRYPTO_GNUTLS"] = False
            tc.variables["REQUIRE_CRYPTO_OPENSSL"] = False
        if self.options.with_ssl == "openssl":
            tc.variables["REQUIRE_CRYPTO_NATIVE"] = False
            tc.variables["REQUIRE_CRYPTO_GNUTLS"] = False
            tc.variables["REQUIRE_CRYPTO_OPENSSL"] = True
        if self.options.with_ssl == "gnutls":
            tc.variables["REQUIRE_CRYPTO_NATIVE"] = False
            tc.variables["REQUIRE_CRYPTO_GNUTLS"] = True
            tc.variables["REQUIRE_CRYPTO_OPENSSL"] = False
        tc.generate()
        # TODO: after https://github.com/conan-io/conan/issues/11962 is solved
        # we might obsolete here cmake deps generation and cmake patching and get
        # the possibility to go for to pkg_config based dependency discovery instead.
        # At the moment, even with the linked work-around, the linkage is mixed-up
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # we generally expect to have one crypto in-place, but need to patch the found mechanics
        # since we avoid currently the correct pkg_config
        replace_in_file(self, os.path.join(self.source_folder, "libqpdf", "CMakeLists.txt"),
                "set(FOUND_CRYPTO OFF)", "set(FOUND_CRYPTO ON)")
        if self.options.with_ssl == "openssl":
            replace_in_file(self, os.path.join(self.source_folder, "libqpdf", "CMakeLists.txt"),
                "set(USE_CRYPTO_OPENSSL OFF)", "set(USE_CRYPTO_OPENSSL ON)")
            replace_in_file(self, os.path.join(self.source_folder, "libqpdf", "CMakeLists.txt"),
                "find_package(ZLIB REQUIRED)",
                "find_package(ZLIB REQUIRED)\nfind_package(OpenSSL REQUIRED)\n")
            replace_in_file(self, os.path.join(self.source_folder, "libqpdf", "CMakeLists.txt"),
                "PUBLIC JPEG::JPEG ZLIB::ZLIB", "PUBLIC JPEG::JPEG ZLIB::ZLIB OpenSSL::SSL")
        if self.options.with_ssl == "gnutls":
            replace_in_file(self, os.path.join(self.source_folder, "libqpdf", "CMakeLists.txt"),
                "set(USE_CRYPTO_GNUTLS OFF)", "set(USE_CRYPTO_GNUTLS ON)")
        if self.options.with_ssl == "internal":
            replace_in_file(self, os.path.join(self.source_folder, "libqpdf", "CMakeLists.txt"),
                "set(USE_CRYPTO_NATIVE OFF)", "set(USE_CRYPTO_NATIVE ON)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "qpdf")
        self.cpp_info.set_property("cmake_target_name", "qpdf::libqpdf")
        self.cpp_info.set_property("pkg_config_name", "libqpdf")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libqpdf"].libs = ["qpdf"]
        self.cpp_info.components["libqpdf"].requires.append("zlib::zlib")
        if self.options.with_jpeg == "libjpeg":
            self.cpp_info.components["libqpdf"].requires.append("libjpeg::libjpeg")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.cpp_info.components["libqpdf"].requires.append("libjpeg-turbo::jpeg")
        elif self.options.with_jpeg == "mozjpeg":
            self.cpp_info.components["libqpdf"].requires.append("mozjpeg::libjpeg")
        if self.options.with_ssl == "openssl":
            self.cpp_info.components["libqpdf"].requires.append("openssl::openssl")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libqpdf"].system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "qpdf"
        self.cpp_info.names["cmake_find_package_multi"] = "qpdf"
        self.cpp_info.components["libqpdf"].names["cmake_find_package"] = "libqpdf"
        self.cpp_info.components["libqpdf"].names["cmake_find_package_multi"] = "libqpdf"
        self.cpp_info.components["libqpdf"].set_property("pkg_config_name", "libqpdf")
        self.cpp_info.components["libqpdf"].set_property("cmake_target_name", "qpdf::libqpdf")
