from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, collect_libs, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class Libssh2Conan(ConanFile):
    name = "libssh2"
    description = "libssh2 is a client-side C library implementing the SSH2 protocol"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libssh2.org"
    topics = ("libssh", "ssh", "shell", "ssh2", "connection")
    license = "BSD-3-Clause"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "enable_crypt_none": [True, False],
        "enable_mac_none": [True, False],
        "crypto_backend": ["openssl", "mbedtls"],
        "enable_debug_logging": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "enable_crypt_none": False,
        "enable_mac_none": False,
        "crypto_backend": "openssl",
        "enable_debug_logging": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _mbedtls_cmake_package_name(self):
        pkg_name = "mbedTLS" if Version(self.version) < "1.11.1" else "MbedTLS"
        return pkg_name

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ENABLE_ZLIB_COMPRESSION"] = self.options.with_zlib
        tc.cache_variables["ENABLE_CRYPT_NONE"] = self.options.enable_crypt_none
        tc.cache_variables["ENABLE_MAC_NONE"] = self.options.enable_mac_none
        tc.cache_variables["ENABLE_DEBUG_LOGGING"] = self.options.enable_debug_logging
        if self.options.crypto_backend == "openssl":
            tc.cache_variables["CRYPTO_BACKEND"] = "OpenSSL"
            tc.cache_variables["OPENSSL_ROOT_DIR"] = self.dependencies["openssl"].package_folder.replace("\\", "/")
        elif self.options.crypto_backend == "mbedtls":
            tc.cache_variables["CRYPTO_BACKEND"] = "mbedTLS"
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables['BUILD_TESTING'] = not self.conf.get("tools.build:skip_test", default=True, check_type=bool)
        tc.cache_variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        # To install relocatable shared lib on Macos by default
        tc.variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # Workaround until github.com/conan-io/conan/pull/12600 is merged
        if is_msvc(self):
            tc.cache_variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = str(self.settings.build_type)
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("mbedtls", "cmake_file_name", self._mbedtls_cmake_package_name)
        deps.set_property("mbedtls", "cmake_additional_variables_prefixes", ["MBEDTLS"])
        deps.generate()

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # This is a pure C library
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.crypto_backend == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        elif self.options.crypto_backend == "mbedtls":
            if Version(self.version) >= "1.11":
                self.requires("mbedtls/3.5.0")
            else:
                self.requires("mbedtls/2.28.4")

    def build_requirements(self):
        if Version(self.version) >= "1.11":
            self.tool_requires("cmake/[>=3.20 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

        cmakelists = os.path.join("src", "CMakeLists.txt") if Version(self.version) <= "1.10" else "CMakeLists.txt"
        replace_in_file(self, os.path.join(self.source_folder, cmakelists), "MBEDTLS_FOUND", f"{self._mbedtls_cmake_package_name}_FOUND")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "share")) # only docs and manpages
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Libssh2")
        self.cpp_info.set_property("cmake_target_name", "Libssh2::libssh2")
        self.cpp_info.set_property("pkg_config_name", "libssh2")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["_libssh2"].libs = collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.components["_libssh2"].system_libs.append("ws2_32")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_libssh2"].system_libs.extend(["pthread", "dl"])

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["_libssh2"].set_property("cmake_target_name", "Libssh2::libssh2")
        self.cpp_info.components["_libssh2"].set_property("pkg_config_name", "libssh2")
        if self.options.with_zlib:
            self.cpp_info.components["_libssh2"].requires.append("zlib::zlib")
        if self.options.crypto_backend == "openssl":
            self.cpp_info.components["_libssh2"].requires.append("openssl::openssl")
        elif self.options.crypto_backend == "mbedtls":
            self.cpp_info.components["_libssh2"].requires.append("mbedtls::mbedtls")
