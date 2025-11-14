from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
)
import os

required_conan_version = ">=2.0.9"


class BoringSSLConan(ConanFile):
    name = "boringssl"
    description = "BoringSSL is a fork of OpenSSL aimed at Google needs."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://boringssl.googlesource.com/boringssl/"
    topics = ("tls", "ssl", "crypto", "openssl", "boringssl")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "openssl_no_asm": [True, False],
        "openssl_small": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "openssl_no_asm": False,
        "openssl_small": False,
    }

    # Remove fPIC when shared=True
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22 <4]")

        # On Windows x86/x64, NASM is needed when assembly is enabled (default).
        # Set -o boringssl:openssl_no_asm=True to avoid NASM.
        if (
            self.settings.os == "Windows"
            and str(self.settings.arch) in ("x86", "x86_64")
            and not self.options.openssl_no_asm
        ):
            self.tool_requires("nasm/2.16.01")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_FIND_PACKAGE_PREFER_CONFIG"] = True

        tc.cache_variables["OPENSSL_NO_ASM"] = bool(self.options.openssl_no_asm)
        tc.cache_variables["OPENSSL_SMALL"] = bool(self.options.openssl_small)

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )

        cmake = CMake(self)
        cmake.install()

        # Intentionally DO NOT remove lib/cmake to preserve the upstream OpenSSL
        # config package so consumers can use: find_package(OpenSSL CONFIG)

    def package_info(self):
        # So consumers can use: find_package(OpenSSL CONFIG)
        self.cpp_info.set_property("cmake_file_name", "OpenSSL")

        # OpenSSL::Crypto
        crypto = self.cpp_info.components["crypto"]
        crypto.set_property("cmake_target_name", "OpenSSL::Crypto")
        crypto.libs = ["crypto"]

        if self.settings.os == "Windows":
            # Upstream adds ws2_32 on Windows
            crypto.system_libs.append("ws2_32")
        elif str(self.settings.os) not in ("Android", "Generic"):
            # Upstream links Threads::Threads on most non-Android/embedded platforms
            crypto.system_libs.append("pthread")

        # OpenSSL::SSL
        ssl = self.cpp_info.components["ssl"]
        ssl.set_property("cmake_target_name", "OpenSSL::SSL")
        ssl.libs = ["ssl"]
        ssl.requires = ["crypto"]
