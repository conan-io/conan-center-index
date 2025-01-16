import os
from pathlib import Path

import yaml
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, rm, rmdir, get
from conan.tools.gnu import GnuToolchain

target_map = {
    ("Android", "armv6", None): "arm-linux-androideabi",
    ("Android", "armv7", None): "armv7-linux-androideabi",
    ("Android", "armv8", None): "aarch64-linux-android",
    ("Android", "x86", None): "i686-linux-android",
    ("Android", "x86_64", None): "x86_64-linux-android",
    ("Emscripten", "wasm", None): "wasm32-unknown-emscripten",
    ("FreeBSD", "x86", None): "i686-unknown-freebsd",
    ("FreeBSD", "x86_64", None): "x86_64-unknown-freebsd",
    ("Linux", "armv6", None): "arm-unknown-linux-gnueabi",
    ("Linux", "armv6hf", None): "arm-unknown-linux-gnueabihf",
    ("Linux", "armv7", None): "armv7-unknown-linux-gnueabi",
    ("Linux", "armv7hf", None): "armv7-unknown-linux-gnueabihf",
    ("Linux", "armv8", None): "aarch64-unknown-linux-gnu",
    ("Linux", "ppc64", None): "powerpc64-unknown-linux-gnu",
    ("Linux", "ppc64le", None): "powerpc64le-unknown-linux-gnu",
    ("Linux", "riscv64", None): "riscv64gc-unknown-linux-gnu",
    ("Linux", "s390x", None): "s390x-unknown-linux-gnu",
    ("Linux", "x86", None): "i686-unknown-linux-gnu",
    ("Linux", "x86_64", None): "x86_64-unknown-linux-gnu",
    ("NetBSD", "x86_64", None): "x86_64-unknown-netbsd",
    ("Solaris", "sparcv9", None): "sparcv9-sun-solaris",
    ("Solaris", "x86_64", None): "x86_64-pc-solaris",
    ("Windows", "armv8", "gcc"): "aarch64-pc-windows-gnullvm",
    ("Windows", "armv8", "msvc"): "aarch64-pc-windows-msvc",
    ("Windows", "x86", "gcc"): "i686-pc-windows-gnu",
    ("Windows", "x86", "msvc"): "i686-pc-windows-msvc",
    ("Windows", "x86_64", "clang"): "x86_64-pc-windows-gnullvm",
    ("Windows", "x86_64", "gcc"): "x86_64-pc-windows-gnu",
    ("Windows", "x86_64", "msvc"): "x86_64-pc-windows-msvc",
    ("apple", "armv8", None): "aarch64-apple-darwin",
    ("apple", "x86_64", None): "x86_64-apple-darwin",
    ("iOS", "armv8", None): "aarch64-apple-ios",
    ("iOS", "x86_64", None): "x86_64-apple-ios",
}


class RustConan(ConanFile):
    name = "rust"
    description = "The Rust Programming Language"
    license = "MIT", "Apache-2.0"
    homepage = "https://www.rust-lang.org"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("rust", "language", "rust-language", "pre-built")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    upload_policy = "skip"
    build_policy = "missing"

    def _settings_to_rust_target(self, settings):
        if settings is None:
            return None
        os = "apple" if settings.os in ["Macos", "watchOS", "tvOS", "visionOS"] else str(settings.os)
        arch = str(settings.arch)
        compiler = str(settings.compiler)
        return target_map.get((os, arch, compiler), target_map.get((os, arch, None)))

    @property
    def _host_rust_target(self):
        return self._settings_to_rust_target(self.settings)

    @property
    def _target_rust_target(self):
        return self._settings_to_rust_target(self.settings_target)

    @property
    def _urls(self):
        return yaml.load(Path(self.recipe_folder, "urls", f"{self.version}.yml").read_text(), Loader=yaml.SafeLoader)

    def export(self):
        copy(self, "urls/*.yml", self.recipe_folder, self.export_folder)

    def layout(self):
        pass

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        urls = self._urls
        host_target = self._host_rust_target
        target_target = self._target_rust_target
        if not self._host_rust_target or self._host_rust_target not in urls["rustc"]:
            raise ConanInvalidConfiguration(f"Unsupported OS/arch combination: {self.settings.os}/{self.settings.arch} ({host_target})")
        if target_target and target_target != host_target and target_target not in urls["stdlib"]:
            raise ConanInvalidConfiguration(
                f"Rust standard library is not available for cross-compilation to {self.settings_target.os}/{self.settings_target.arch} ({target_target})"
            )

    def build(self):
        urls = self._urls
        host_target = self._settings_to_rust_target(self.settings)
        target_target = self._settings_to_rust_target(self.settings_target)
        get(self, **urls["rustc"][host_target], strip_root=True, destination="rustc")
        if target_target and target_target != host_target:
            get(self, **urls["stdlib"][target_target], strip_root=True, destination="stdlib")

    def package(self):
        copy(self, "LICENSE-*", self.build_folder, os.path.join(self.package_folder, "licenses"))

        # Merge all Rust components into the package folder
        for path in Path(self.build_folder, "rustc").iterdir():
            if path.is_dir() and "docs" not in path.name:
                self.output.info(f"Copying {path.name} contents to {self.package_folder}")
                copy(self, "*", path, self.package_folder)

        # Copy the target standard library for cross-compilation
        host_target = self._settings_to_rust_target(self.settings)
        target_target = self._settings_to_rust_target(self.settings_target)
        if target_target and target_target != host_target:
            copy(self, "*",
                 os.path.join(self.build_folder, "stdlib", f"rust-std-{target_target}", "lib"),
                 os.path.join(self.package_folder, "lib"))

        rm(self, "manifest.in", self.package_folder)
        rm(self, "*.pdb", self.package_folder, recursive=True)
        rmdir(self, os.path.join(self.package_folder, "libexec"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []

        # https://doc.rust-lang.org/cargo/reference/environment-variables.html
        self.buildenv_info.define_path("CARGO", os.path.join(self.package_folder, "bin", "cargo"))
        self.buildenv_info.define_path("RUSTC", os.path.join(self.package_folder, "bin", "rustc"))
        self.buildenv_info.define_path("RUSTDOC", os.path.join(self.package_folder, "bin", "rustdoc"))
        self.buildenv_info.define_path("RUSTFMT", os.path.join(self.package_folder, "bin", "rustfmt"))

        # Ensure the correct linker is used
        host_target = self._host_rust_target
        gnu_vars = GnuToolchain(self).extra_env.vars(self)
        cc = gnu_vars["CC"].replace("\\", "/")
        target_upper = host_target.upper().replace("-", "_")
        self.buildenv_info.define_path(f"CARGO_TARGET_{target_upper}_LINKER", cc)

        # Define the cross-build target, if applicable
        target_target = self._target_rust_target
        if target_target and target_target != host_target:
            self.buildenv_info.define("CARGO_BUILD_TARGET", target_target)
            # FIXME: Conan currently does not provide a way to get the actual compiler path
            cc = str(self.settings_target.compiler)
            target_upper = host_target.upper().replace("-", "_")
            self.buildenv_info.define_path(f"CARGO_TARGET_{target_upper}_LINKER", cc)
            self.conf_info.define("user.rust:target", target_target)
        else:
            self.conf_info.define("user.rust:target", host_target)
