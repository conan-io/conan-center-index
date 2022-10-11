from pathlib import PureWindowsPath
import os.path
import sys

from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get, rename, replace_in_file
from conan.tools.microsoft import is_msvc


class RustConan(ConanFile):
    name = "rust"
    description = "The Rust Programming Language"
    license = "Apache-2.0"
    topics = ("rust", "language", "rust-language")
    homepage = "https://www.rust-lang.org"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    generators = "PkgConfigDeps", "VirtualBuildEnv"
    short_paths = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def build_requirements(self):
        self.tool_requires("ninja/1.11.0")
        self.tool_requires("openssl/3.0.5")
        self.tool_requires("pkgconf/1.9.3")

    @property
    def _windows_build_triple(self):
        suffix = "msvc" if is_msvc(self) else "gnu"
        return f"{str(self.settings.arch)}-pc-windows-{suffix}"

    def _configure_sources(self):
        config_file = os.path.join(self.source_folder, "config.toml.example")

        def unix_path(path):
            if self.settings.os == "Windows":
                return PureWindowsPath(path).as_posix()
            return path

        def config(value, replacement):
            replace_in_file(
                self,
                config_file,
                value,
                replacement
            )
        install_folder = unix_path(os.path.join(self.package_folder, "bin"))
        config('#prefix = "/usr/local"', f'prefix = "{install_folder}"')
        config('#docs = true', 'docs = false')
        rename(self, config_file, os.path.join(self.source_folder, "config.toml"))

    @property
    def _python_interpreter(self):
        if getattr(sys, "frozen", False):
            return "python"
        return sys.executable

    def _xpy_command(self, mode):
        cmd = f"{self._python_interpreter} x.py {mode}"
        if self.settings.os == "Windows":
            cmd += f" --build={self._windows_build_triple}"
        return cmd

    def build(self):
        self._configure_sources()
        self.run(self._xpy_command("build"), cwd=self.source_folder)

    def package(self):
        self.run(self._xpy_command("install"), cwd=self.source_folder)
        licenses_folder = os.path.join(self.package_folder, "licenses")
        copy(self, "LICENSE-APACHE", self.source_folder, licenses_folder)
        copy(self, "LICENSE-MIT", self.source_folder, licenses_folder)

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        bin_path = os.path.join(self.package_folder, "bin", "bin")
        self.output.info("Appending PATH environment variable:: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type
