import os.path
import sys
import textwrap

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path


class RustConan(ConanFile):
    name = "rust"
    description = "The Rust Programming Language"
    license = "Apache-2.0"
    homepage = "https://www.rust-lang.org"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("rust", "language", "rust-language")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    short_paths = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]", visible=False)

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def build_requirements(self):
        self.tool_requires("ninja/1.11.1")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _config_toml_path(self):
        return os.path.join(self.generators_folder, "config.toml")

    def _write_config_toml(self):
        install_folder = unix_path(self, os.path.join(self.package_folder, "bin"))
        with open(self._config_toml_path, "w", encoding="utf8") as f:
            f.write(textwrap.dedent(f"""\
                [build]
                docs = false
                [install]
                prefix = "{install_folder}"
                [rust]
                rpath = false
            """))

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()
        deps = PkgConfigDeps(self)
        deps.generate()
        self._write_config_toml()

    @property
    def _python_interpreter(self):
        if getattr(sys, "frozen", False):
            return "python"
        return sys.executable

    @property
    def _windows_build_triple(self):
        suffix = "msvc" if is_msvc(self) else "gnu"
        return f"{str(self.settings.arch)}-pc-windows-{suffix}"

    def _xpy(self, mode):
        # x.py is the build tool for the rust repository
        cmd = f"{self._python_interpreter} x.py {mode} --config {self._config_toml_path}"
        if self.settings.os == "Windows":
            cmd += f" --build={self._windows_build_triple}"
        return self.run(cmd, cwd=self.source_folder)

    def build(self):
        self._xpy("build")

    def package(self):
        copy(self, "LICENSE-APACHE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE-MIT", self.source_folder, os.path.join(self.package_folder, "licenses"))
        self._xpy("install")

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
