from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, collect_libs
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"


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

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_ZLIB_COMPRESSION"] = self.options.with_zlib
        tc.variables["ENABLE_CRYPT_NONE"] = self.options.enable_crypt_none
        tc.variables["ENABLE_MAC_NONE"] = self.options.enable_mac_none
        tc.variables["ENABLE_DEBUG_LOGGING"] = self.options.enable_debug_logging
        if self.options.crypto_backend == "openssl":
            tc.variables["CRYPTO_BACKEND"] = "OpenSSL"
            tc.variables["OPENSSL_ROOT_DIR"] = self.dependencies["openssl"].package_folder.replace("\\", "/")
        elif self.options.crypto_backend == "mbedtls":
            tc.variables["CRYPTO_BACKEND"] = "mbedTLS"
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables['BUILD_TESTING'] = not self.conf.get("tools.build:skip_test", default=True, check_type=bool)
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        # To install relocatable shared lib on Macos by default
        tc.variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # Workaround until github.com/conan-io/conan/pull/12600 is merged
        if is_msvc(self):
            tc.cache_variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = str(self.settings.build_type)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.settings.os != "Windows":
            del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def requirements(self):
        self.requires(self.tested_reference_str)
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
        if self.options.crypto_backend == "openssl":
            self.requires("openssl/1.1.1t")
            # Version 3.x not currently working
            # self.requires("openssl/[>=1.1 <4]")
        elif self.options.crypto_backend == "mbedtls":
            # libssh2/<=1.10.0 doesn't support mbedtls/3.x.x
            self.requires("mbedtls/2.25.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"), keep_path=False)
        copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["libssh2"]
        self.cpp_info.set_property("cmake_file_name", "libssh2")
        self.cpp_info.set_property("cmake_target_name", "libssh2::libssh2")
        self.cpp_info.set_property("cmake_module_file_name", "libssh2")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("pkg_config_name", "libssh2")

        self.cpp_info.components["libssh2"].libs = collect_libs(self)

        if self.options.crypto_backend == "openssl":
            self.cpp_info.components["libssh2"].requires.append("openssl::openssl")
        elif self.options.crypto_backend == "mbedtls":
            self.cpp_info.components["libssh2"].requires.append("mbedtls::mbedtls")
        if self.options.with_zlib:
            self.cpp_info.components["libssh2"].requires.append("zlib::zlib")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "dl"])
