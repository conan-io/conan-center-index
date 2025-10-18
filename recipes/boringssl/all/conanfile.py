from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
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
        "fips": [True, False],
        "asan": [True, False],
        "msan": [True, False],
        "tsan": [True, False],
        "ubsan": [True, False],
        "ubsan_recover": [True, False],
        "cfi": [True, False],
        "openssl_no_asm": [True, False],
        "openssl_small": [True, False],
        "boringssl_allow_cxx_runtime": [True, False],
        "rust_bindings": [True, False],
        "build_testing": [True, False],
        "fuzz": [True, False],
        "libfuzzer_from_deps": [True, False],
        "boringssl_prefix": [None, "ANY"],
        "boringssl_prefix_symbols": [None, "ANY"],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "fips": False,
        "asan": False,
        "msan": False,
        "tsan": False,
        "ubsan": False,
        "ubsan_recover": False,
        "cfi": False,
        "openssl_no_asm": False,
        "openssl_small": False,
        "boringssl_allow_cxx_runtime": False,
        "rust_bindings": False,
        "build_testing": False,
        "fuzz": False,
        "libfuzzer_from_deps": False,
        "boringssl_prefix": None,
        "boringssl_prefix_symbols": None,
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

        # Go is required by upstream for:
        # - FIPS support
        # - symbol prefix generation (BORINGSSL_PREFIX_SYMBOLS)
        if (
            self.options.fips
            or self.options.boringssl_prefix
            or self.options.build_testing
        ):
            raise ConanInvalidConfiguration(
                "fips=True, boringssl_prefix=True, build_testing=True are not supported in ConanCenter (go is not packaged)."
            )
            # self.tool_requires("go/[>=1.21 <2]")

    def validate(self):
        check_min_cppstd(self, 17)

        compiler = str(self.settings.compiler)
        using_clang = compiler in ("clang", "apple-clang")

        if self.options.cfi and not using_clang:
            raise ConanInvalidConfiguration("cfi=True requires Clang.")
        if self.options.asan and not using_clang:
            raise ConanInvalidConfiguration("asan=True requires Clang.")
        if self.options.msan and not using_clang:
            raise ConanInvalidConfiguration("msan=True requires Clang.")
        if self.options.tsan and not using_clang:
            raise ConanInvalidConfiguration("tsan=True requires Clang.")
        if self.options.ubsan and not using_clang:
            raise ConanInvalidConfiguration("ubsan=True requires Clang.")

        if self.options.asan and self.options.msan:
            raise ConanInvalidConfiguration("asan and msan are mutually exclusive.")

        if (
            self.options.boringssl_prefix and not self.options.boringssl_prefix_symbols
        ) or (
            self.options.boringssl_prefix_symbols and not self.options.boringssl_prefix
        ):
            raise ConanInvalidConfiguration(
                "boringssl_prefix and boringssl_prefix_symbols must be specified together."
            )

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_FIND_PACKAGE_PREFER_CONFIG"] = True

        tc.cache_variables["FIPS"] = bool(self.options.fips)

        tc.cache_variables["ASAN"] = bool(self.options.asan)
        tc.cache_variables["MSAN"] = bool(self.options.msan)
        tc.cache_variables["TSAN"] = bool(self.options.tsan)
        tc.cache_variables["UBSAN"] = bool(self.options.ubsan)
        tc.cache_variables["UBSAN_RECOVER"] = bool(self.options.ubsan_recover)

        tc.cache_variables["CFI"] = bool(self.options.cfi)

        tc.cache_variables["OPENSSL_NO_ASM"] = bool(self.options.openssl_no_asm)
        tc.cache_variables["OPENSSL_SMALL"] = bool(self.options.openssl_small)

        # Disables -fno-exceptions/-fno-rtti restrictions
        tc.cache_variables["BORINGSSL_ALLOW_CXX_RUNTIME"] = bool(
            self.options.boringssl_allow_cxx_runtime
        )

        tc.cache_variables["RUST_BINDINGS"] = bool(self.options.rust_bindings)

        tc.cache_variables["BUILD_TESTING"] = bool(self.options.build_testing)
        tc.cache_variables["FUZZ"] = bool(self.options.fuzz)
        tc.cache_variables["LIBFUZZER_FROM_DEPS"] = bool(
            self.options.libfuzzer_from_deps
        )

        if self.options.boringssl_prefix:
            tc.cache_variables["BORINGSSL_PREFIX"] = str(self.options.boringssl_prefix)
        if self.options.boringssl_prefix_symbols:
            tc.cache_variables["BORINGSSL_PREFIX_SYMBOLS"] = str(
                self.options.boringssl_prefix_symbols
            )

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
