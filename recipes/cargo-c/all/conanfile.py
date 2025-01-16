import os
from pathlib import Path

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.env import Environment
from conan.tools.files import copy, get
from conan.tools.gnu import GnuToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout

required_conan_version = ">=2.0"


class CargoCConan(ConanFile):
    name = "cargo-c"
    description = "Rust cargo applet to build and install C-ABI compatible dynamic and static libraries"
    license = "MIT"
    homepage = "https://github.com/lu-zero/cargo-c"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("rust", "cargo")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def configure(self):
        del self.settings.compiler

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")
        # self.requires("libnghttp2/1.61.0")
        self.requires("zlib/[>=1.2.13 <2]")
        # self.requires("libssh2/1.11.0")
        self.requires("libgit2/1.8.4")
        self.requires("libcurl/[>=7.78.0 <9]")

    def build_requirements(self):
        self.tool_requires("rust/1.84.0")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _define_rust_env(self, env, scope="host", cflags=None):
        target = self.conf.get(f"user.rust:target_{scope}", check_type=str).replace("-", "_")
        cc = GnuToolchain(self).extra_env.vars(self)["CC" if scope == "host" else "CC_FOR_BUILD"]
        env.define_path(f"CARGO_TARGET_{target.upper()}_LINKER", cc)
        env.define_path(f"CC_{target}", cc)
        if cflags:
            env.append(f"CFLAGS_{target}", cflags)

    def generate(self):
        env = Environment()
        openssl = self.dependencies["openssl"].cpp_info
        self._define_rust_env(env, "host", cflags=f" -I{openssl.includedir} -L{openssl.libdir} -lssl -lcrypto")
        if cross_building(self):
            self._define_rust_env(env, "build")
        env.define_path("CARGO_HOME", os.path.join(self.build_folder, "cargo"))
        env.prepend_path("PKG_CONFIG_PATH", self.generators_folder)
        # libssh2 fails to build otherwise
        # https://github.com/alexcrichton/ssh2-rs/blob/libssh2-sys-0.3.0/libssh2-sys/build.rs#L19-L23
        env.define("LIBSSH2_SYS_USE_PKG_CONFIG", "1")
        env.define("CC_FORCE_DISABLE", "1")
        env.define("OPENSSL_NO_VENDOR", "1")
        env.vars(self).save_script("cargo_paths")

        deps = PkgConfigDeps(self)
        deps.generate()

    @property
    def _build_type_flag(self):
        return "" if self.settings.build_type == "Debug" else "--release"

    def build(self):
        self.run(f"cargo rustc -p cargo-c {self._build_type_flag} --target-dir {self.build_folder}", cwd=self.source_folder)

    @property
    def _dist_dir(self):
        build_type = "debug" if self.settings.build_type == "Debug" else "release"
        if cross_building(self):
            platform = self.conf.get("user.rust:target_host", check_type=str)
            return Path(self.build_folder, platform, build_type)
        return Path(self.build_folder, build_type)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        for f in ["cargo-capi", "cargo-cbuild", "cargo-cinstall", "cargo-ctest"]:
            ext = ".exe" if self.settings.os == "Windows" else ""
            copy(self, f + ext, self._dist_dir, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
