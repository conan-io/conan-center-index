import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import collect_libs, copy, get, rmdir

required_conan_version = ">=1.47.0"


class LibSSHRecipe(ConanFile):
    name = "libssh"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libssh.org/"
    description = "multiplatform C library implementing the SSHv2 protocol on client and server side"
    topics = ("ssh", "shell", "ssh2", "connection")

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

    def configures(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.crypto_backend =="openssl":
            self.requires("openssl/1.1.1q")
        elif self.options.crypto_backend == "gcrypt":
            self.requires("libgcrypt/1.8.4")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CLIENT_TESTING"] = False
        tc.variables["SERVER_TESTING"] = False
        tc.variables["WITH_GSSAPI"] = False
        tc.variables["WITH_ZLIB"] = self.options.with_zlib
        tc.variables["WITH_GCRYPT"] = self.options.crypto_backend == "gcrypt"
        tc.variables["WITH_MBEDTLS"] = False
        tc.variables["WITH_EXAMPLES"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libssh")
        self.cpp_info.set_property("cmake_target_name", "libssh::libssh")
        self.cpp_info.set_property("pkg_config_name", "libssh")
        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["_libssh"].libs = collect_libs(self)
        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "libssh"
        self.cpp_info.names["cmake_find_package_multi"] = "libssh"
        self.cpp_info.components["_libssh"].names["cmake_find_package"] = "libssh"
        self.cpp_info.components["_libssh"].names["cmake_find_package_multi"] = "libssh"
        self.cpp_info.components["_libssh"].set_property("cmake_target_name", "libssh::libssh")
        self.cpp_info.components["_libssh"].set_property("pkg_config_name", "libssh")
        if self.options.with_zlib:
            self.cpp_info.components["_libssh"].requires.append("zlib::zlib")
        if self.options.crypto_backend == "openssl":
            self.cpp_info.components["_libssh"].requires.append("openssl::openssl")
        elif self.options.crypto_backend == "gcrypt":
            self.cpp_info.components["_libssh"].requires.append("libgcrypt::libgcrypt")
