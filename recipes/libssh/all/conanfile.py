from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
import os


required_conan_version = ">=1.53.0"


class LibSSHRecipe(ConanFile):
    name = "libssh"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libssh.org/"
    description = "multiplatform C library implementing the SSHv2 protocol on client and server side"
    topics = ("ssh", "shell", "ssh2", "connection")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "crypto_backend": ["openssl", "gcrypt"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "crypto_backend": "openssl",
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
        if self.options.crypto_backend =="openssl":
            self.requires("openssl/1.1.1t")
        elif self.options.crypto_backend == "gcrypt":
            self.requires("libgcrypt/1.8.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CLIENT_TESTING"] = False
        tc.variables["SERVER_TESTING"] = False
        tc.variables["WITH_EXAMPLES"] = False
        tc.variables["WITH_GCRYPT"] = self.options.crypto_backend == "gcrypt"
        tc.variables["WITH_GSSAPI"] = False
        tc.variables["WITH_MBEDTLS"] = False
        tc.variables["WITH_NACL"] = False
        tc.variables["WITH_SYMBOL_VERSIONING"] = False
        tc.variables["WITH_ZLIB"] = self.options.with_zlib
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        # work-around conan-io/conan-center-index#16900
        replace_in_file(self, os.path.join(self.source_folder, "ConfigureChecks.cmake"), "${OPENSSL_CRYPTO_LIBRARIES}", "OpenSSL::Crypto")
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"), "${OPENSSL_CRYPTO_LIBRARIES}", "OpenSSL::Crypto")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["ssh"]

        self.cpp_info.set_property("cmake_file_name", "libssh")
        self.cpp_info.set_property("cmake_target_name", "ssh")
        self.cpp_info.set_property("pkg_config_name", "libssh")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "libssh"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libssh"
        self.cpp_info.names["cmake_find_package"] = "libssh"
        self.cpp_info.names["cmake_find_package_multi"] = "libssh"
