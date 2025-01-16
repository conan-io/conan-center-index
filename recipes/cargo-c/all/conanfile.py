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

    def build_requirements(self):
        self.tool_requires("rust/1.84.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = Environment()
        # Ensure the correct linker is used, especially when cross-compiling
        target_upper = self.conf.get("user.rust:target", check_type=str).upper().replace("-", "_")
        cc = GnuToolchain(self).extra_env.vars(self)["CC"]
        env.define_path(f"CARGO_TARGET_{target_upper}_LINKER", cc)
        # Don't add the Cargo dependencies to a global Cargo cache
        env.define_path("CARGO_HOME", os.path.join(self.build_folder, "cargo"))
        env.append_path("PKG_CONFIG_PATH", self.generators_folder)
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
            platform = self.conf.get("user.rust:target", check_type=str)
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
