from conan import ConanFile
from conan.errors import ConanException
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import build_jobs
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, replace_in_file, rename, rm, rmdir
from conan.tools.gnu import AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

import os


required_conan_version = ">=2.25"

class OpenSSLConan(ConanFile):
    name = "openssl"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/openssl/openssl"
    license = "Apache-2.0"
    topics = ("ssl", "tls", "encryption", "security")
    description = "A toolkit for the Transport Layer Security (TLS) and Secure Sockets Layer (SSL) protocols"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "no_fips": [True, False],
        "openssldir": [None, "ANY"],
        "extra_build_opts": [None, "ANY"], # comma separated 
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "no_fips": False,
        "openssldir": None,
        "extra_build_opts": None,
    }

    @property
    def _is_mingw(self):
        is_gcc = self.settings.compiler == "gcc"
        is_clang = self.settings.compiler == "clang" and self.settings.compiler.get_safe("runtime") is None
        return self.settings.os == "Windows" and (is_gcc or is_clang)

    @property
    def _msvc_abi(self):
        return self.settings.os == "Windows" and self.settings.compiler.get_safe("runtime")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self.settings_build.os == "Windows" and self._msvc_abi:
            self.tool_requires("jom/[*]")
            self.tool_requires("strawberryperl/[>=5.32 <6]")
            if self.settings.arch in ["x86", "x86_64"]:
                self.tool_requires("nasm/[*]")
        else:
            self.win_bash = True

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    @property
    def _target(self):
        # Map the Conan os/arch to a built-in OpenSSL Configure target (see `./Configure LIST`).
        # Conan's "armv8" is arm64/aarch64. Anything not listed must be supplied explicitly
        # via the user.openssl:target conf.     
        custom_target = self.conf.get("user.openssl:target", check_type=str)
        if custom_target:
            return custom_target
        
        targets = {
            ("Android", "armv8"): "android-arm64",
            ("Linux", "x86_64"): "linux-x86_64",
            ("Linux", "armv8"): "linux-aarch64",
            ("Macos", "x86_64"): "darwin64-x86_64-cc",
            ("Macos", "armv8"): "darwin64-arm64-cc",
            ("iOS", "x86_64"): "iossimulator-x86_64-xcrun",
            ("iOS", "armv8"): "ios64-xcrun",
            ("Windows", "x86_64"): "mingw64" if self._is_mingw else "VC-WIN64A",
            ("Windows", "armv8"): (
                "mingwarm64" if self._is_mingw
                else "VC-CLANG-WIN64-CLANGASM-ARM" if self.settings.compiler == "clang" and self._msvc_abi
                else "VC-WIN64-CLANGASM-ARM"
            ),
        }
        key = (str(self.settings.os), str(self.settings.arch))
        if key not in targets:
            raise ConanException(
                f"Unable to map configuration for {key[0]}/{key[1]}.\n"
                f"Set the user.openssl:target configuration to a built-in "
                f"OpenSSL target to override, or open an issue at {self.url}."
            )
        return targets[key]

    def generate(self):
        tc = AutotoolsToolchain(self)
        if is_msvc(self):
            tc.extra_cflags.append("-nologo")
        if is_apple_os(self) and self.options.shared:
            tc.extra_ldflags.append("-headerpad_max_install_names")
        tc.generate()

    @property
    def _configure_args(self):
        args = [
            f'"{self._target}"',
            "shared" if self.options.shared else "no-shared",
            "--debug" if self.settings.build_type == "Debug" else "--release",
            "no-fips" if self.options.no_fips else "enable-fips",
            "--prefix=C:/" if self._msvc_abi else "--prefix=/",
            f"-D__ANDROID_API__={str(self.settings.os.api_level)}" if self.settings.os == "Android" else "",
            "enable-static-vcruntime" if self.settings.get_safe("compiler.runtime") == "static" else "",
            "--libdir=lib",
            "no-docs",
            "no-unit-test",
            "no-tests",
        ]

        if self.settings.os != "Windows":
            args.append("-fPIC" if self.options.get_safe("fPIC", True) else "no-pic")

        if self.options.extra_build_opts:
            args.extend(flag.strip() for flag in str(self.options.extra_build_opts).split(",") if flag.strip())

        return args
    
    @property
    def _make_program(self):
        if self._msvc_abi:
            return "jom"
        else:
            return self.conf.get("tools.gnu:make_program", default="make")

    def build(self):
        args = " ".join(self._configure_args)
        perl = "perl" if "strawberryperl" in self.dependencies.build else ""
        configure = os.path.join(self.source_folder, "Configure").replace('\\', '/')
        self.run(f'{perl} "{configure}" {args}', env="conanbuild")
        self.run(f"{perl} ./configdata.pm --dump", env="conanbuild")
        self.run(f"{self._make_program} -j{build_jobs(self)}", env="conanbuild")
        if self._msvc_abi:
            # patch generated Makefile not correctly escaping a backslash
            replace_in_file(self, "Makefile", "INSTALLTOP_dir=\\", "INSTALLTOP_dir=/")
        if not self._msvc_abi and self.options.shared:
            # supress installation of static libs when shared is enabled
            replace_in_file(self, "Makefile", "INSTALL_LIBS=libcrypto.a libssl.a", "INSTALL_LIBS=")

    def package(self):
        copy(self, "*LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        destdir = self.package_folder.replace('\\', '/')
        self.run(f'{self._make_program} install -j1 DESTDIR="{destdir}"', env="conanbuild")
        if is_apple_os(self):
            fix_apple_shared_install_name(self)
        if self._msvc_abi:
            rename(self, os.path.join(self.package_folder, "Program Files/Common Files/SSL"),
                        os.path.join(self.package_folder, "ssl"))

        rm(self, "*.pdb", self.package_folder, "lib")
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenSSL")
        self.cpp_info.set_property("pkg_config_name", "openssl")

        # Align with the definitions from CMake's FindOpenSSL module
        self.cpp_info.set_property("cmake_additional_variables_prefixes", ["OPENSSL"])
        self.cpp_info.set_property("cmake_extra_variables", {'OPENSSL_FOUND': 'TRUE',
                                                             'OPENSSL_VERSION': self.version,
                                                             'OPENSSL_CRYPTO_LIBRARY': 'OpenSSL::Crypto',
                                                             'OPENSSL_CRYPTO_LIBRARIES': 'OpenSSL::Crypto',
                                                             'OPENSSL_SSL_LIBRARY': 'OpenSSL::SSL',
                                                             'OPENSSL_SSL_LIBRARIES': 'OpenSSL::SSL',
                                                             'OPENSSL_LIBRARIES': 'OpenSSL::SSL;OpenSSL::Crypto'})
        
        prefix = "lib" if self._msvc_abi else ""
        self.cpp_info.components["ssl"].libs = [f"{prefix}ssl"]
        self.cpp_info.components["crypto"].libs = [f"{prefix}crypto"]
        self.cpp_info.components["ssl"].requires = ["crypto"]

        if self.settings.os == "Windows":
            self.cpp_info.components["crypto"].system_libs.extend(["crypt32", "ws2_32", "advapi32", "user32", "bcrypt"])
        elif self.settings.os == "Linux":
            self.cpp_info.components["crypto"].system_libs.extend(["dl", "rt", "pthread"])
            self.cpp_info.components["ssl"].system_libs.extend(["dl", "pthread"])

        self.cpp_info.components["crypto"].set_property("cmake_target_name", "OpenSSL::Crypto")
        self.cpp_info.components["crypto"].set_property("pkg_config_name", "libcrypto")
        self.cpp_info.components["ssl"].set_property("cmake_target_name", "OpenSSL::SSL")
        self.cpp_info.components["ssl"].set_property("pkg_config_name", "libssl")

        openssl_modules_dir = os.path.join(self.package_folder, "lib", "ossl-modules")
        self.runenv_info.define_path("OPENSSL_MODULES", openssl_modules_dir)
