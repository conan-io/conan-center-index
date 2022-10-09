from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.files import patch, export_conandata_patches, get, copy, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc, check_min_vs
from conan.tools.gnu import PkgConfigDeps
from conan.tools.env import VirtualBuildEnv, Environment
import os

required_conan_version = ">=1.52.0"

class PackageConan(ConanFile):
    name = "qpdf"
    description = "QPDF is a command-line tool and C++ library that performs content-preserving transformations on PDF files."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/qpdf/qpdf"
    topics = ("pdf")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_crypto": ["native", "openssl", "gnutls"],
        "with_jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_crypto": "native",
        "with_jpeg": "libjpeg",
    }

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # https://qpdf.readthedocs.io/en/stable/installation.html#basic-dependencies
        self.requires("zlib/1.2.12")
        if self.options.with_crypto == "openssl":
            self.requires("openssl/1.1.1q")
        elif self.options.with_crypto == "gnutls":
            raise ConanInvalidConfiguration("GnuTLS is not available in Conan Center yet.")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.4")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.0.0")


    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        if is_msvc(self):
            check_min_vs(self, "150")
        else:
            minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
            if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support.")

    def build_requirements(self):
        self.tool_requires("cmake/3.24.1")
        self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        # https://qpdf.readthedocs.io/en/latest/installation.html#build-time-crypto-selection
        tc.variables["USE_IMPLICIT_CRYPTO"] = False
        tc.cache_variables["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = True
        if self.options.with_crypto == "native":
            tc.variables["REQUIRE_CRYPTO_NATIVE"] = True
            tc.variables["REQUIRE_CRYPTO_GNUTLS"] = False
            tc.variables["REQUIRE_CRYPTO_OPENSSL"] = False
        elif self.options.with_crypto == "openssl":
            tc.variables["REQUIRE_CRYPTO_NATIVE"] = False
            tc.variables["REQUIRE_CRYPTO_GNUTLS"] = False
            tc.variables["REQUIRE_CRYPTO_OPENSSL"] = True
        tc.generate()
        # TODO: after https://github.com/conan-io/conan/issues/11962 is solved
        # we might obsolete here cmake deps generation and cmake patching and get
        # the possibility to go for to pkg_config based dependency discovery instead.
        # At the moment, even with the linked work-around, the linkage is mixed-up
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def _patch_sources(self):
        # patch 0001 and 0002 are uniquely appliable, based ony dependency config
        patches_to_apply = ["0003-exclude-unnecessary-cmake-subprojects.patch"]
        if self.options.with_crypto == "openssl":
            patches_to_apply.append("0002-libqpdf-cmake-deps-jpeg-zlib-openssl.patch")
        else:
            patches_to_apply.append("0001-libqpdf-cmake-deps-jpeg-zlib.patch")
        for patch_file in patches_to_apply:
            patch(self, base_path=self.source_folder,
                  patch_file=os.path.join(self.source_folder, "..", "patches", patch_file))

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

    def self.package_info(self):
        self.cpp_info.set_property("cmake_file_name", "qpdf")

        self.cpp_info.components["libqpdf"].libs = ["qpdf"]
        self.cpp_info.components["libqpdf"].set_property("pkg_config_name", "libqpdf")
        self.cpp_info.components["libqpdf"].set_property("cmake_target_name", "qpdf::libqpdf")
        self.cpp_info.components["libqpdf"].requires.append("zlib::zlib")
        self.cpp_info.components["libqpdf"].requires.append(f"{self.options.with_jpeg}::{self.options.with_jpeg}")

        if self.options.with_crypto == "openssl":
            self.cpp_info.components["libqpdf"].requires.append("openssl::openssl")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libqpdf"].system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "qpdf"
        self.cpp_info.filenames["cmake_find_package_multi"] = "qpdf"
        self.cpp_info.names["cmake_find_package"] = "qpdf"
        self.cpp_info.names["cmake_find_package_multi"] = "qpdf"
        self.cpp_info.components["libqpdf"].names["cmake_find_package"] = "libqpdf"
        self.cpp_info.components["libqpdf"].names["cmake_find_package_multi"] = "libqpdf"
