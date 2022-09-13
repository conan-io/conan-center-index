from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.3"


class AwsCCal(ConanFile):
    name = "aws-c-cal"
    description = "Aws Crypto Abstraction Layer: Cross-Platform, C99 wrapper for cryptography primitives."
    topics = ("aws", "amazon", "cloud", "cal", "crypt", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-cal"
    license = "Apache-2.0",
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _needs_openssl(self):
        return self.settings.os != "Windows" and not is_apple_os(self)

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) <= "0.5.11":
            self.requires("aws-c-common/0.6.11")
        else:
            self.requires("aws-c-common/0.7.4")
        if self._needs_openssl:
            self.requires("openssl/1.1.1q")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["USE_OPENSSL"] = self._needs_openssl
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-cal"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-cal")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-cal")

        self.cpp_info.filenames["cmake_find_package"] = "aws-c-cal"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-cal"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-cal-lib"].names["cmake_find_package"] = "aws-c-cal"
        self.cpp_info.components["aws-c-cal-lib"].names["cmake_find_package_multi"] = "aws-c-cal"
        self.cpp_info.components["aws-c-cal-lib"].set_property("cmake_target_name", "AWS::aws-c-cal")

        self.cpp_info.components["aws-c-cal-lib"].libs = ["aws-c-cal"]
        self.cpp_info.components["aws-c-cal-lib"].requires = ["aws-c-common::aws-c-common-lib"]
        if self.settings.os == "Windows":
            self.cpp_info.components["aws-c-cal-lib"].system_libs.append("ncrypt")
        elif is_apple_os(self):
            self.cpp_info.components["aws-c-cal-lib"].frameworks.append("Security")
        elif self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["aws-c-cal-lib"].system_libs.append("dl")

        self.user_info.with_openssl = self._needs_openssl
        if self._needs_openssl:
            self.cpp_info.components["aws-c-cal-lib"].requires.append("openssl::crypto")
            if not self.dependencies["openssl"].options.shared:
                # aws-c-cal does not statically link to openssl and searches dynamically for openssl symbols .
                # Mark these as undefined so the linker will include them.
                # This avoids dynamical look-up for a system crypto library.
                crypto_symbols = [
                    "HMAC_Update", "HMAC_Final", "HMAC_Init_ex",
                ]
                if Version(self.dependencies["openssl"].ref.version) >= "1.1":
                    crypto_symbols.extend([
                        "HMAC_CTX_new", "HMAC_CTX_free", "HMAC_CTX_reset",
                    ])
                else:
                    crypto_symbols.extend([
                        "HMAC_CTX_init", "HMAC_CTX_cleanup", "HMAC_CTX_reset",
                    ])
                crypto_link_flags = "-Wl," + ",".join(f"-u{symbol}" for symbol in crypto_symbols)
                self.cpp_info.components["aws-c-cal-lib"].exelinkflags.append(crypto_link_flags)
                self.cpp_info.components["aws-c-cal-lib"].sharedlinkflags.append(crypto_link_flags)
