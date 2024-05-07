import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import copy, get, save
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version

required_conan_version = ">=1.60.0 <2 || >=2.0.6"


class NumpyConan(ConanFile):
    name = "numpy"
    description = "NumPy is the fundamental package for scientific computing with Python."
    license = "BSD 3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://numpy.org/devdocs/reference/c-api/index.html"
    topics = ("ndarray", "array", "linear algebra", "npymath")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    short_paths = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
    
    def validate(self):
        # https://github.com/numpy/numpy/blob/v1.26.4/meson.build#L28
        if self.settings.compiler == "gcc" and self.settings.compiler.version < Version("8.4"):
            raise ConanInvalidConfiguration(f"{self.ref} requires GCC 8.4+")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openblas/0.3.26")
        self.requires("cpython/3.12.2", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("cpython/<host_version>")
        self.tool_requires("ninja/1.11.1")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _meson_root(self):
        return self.source_path.joinpath("vendored-meson", "meson")

    @property
    def _build_site_packages(self):
        return os.path.join(self.build_folder, "site-packages")

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        env = Environment()
        # NumPy can only be built with its vendored Meson
        env.prepend_path("PATH", str(self._meson_root))
        env.prepend_path("PYTHONPATH", self._build_site_packages)
        env.prepend_path("PATH", os.path.join(self._build_site_packages, "bin"))
        env.vars(self).save_script("conanbuild_paths")

        tc = MesonToolchain(self)
        tc.project_options["allow-noblas"] = False
        tc.project_options["blas-order"] = ["openblas"]
        tc.project_options["lapack-order"] = ["openblas"]
        tc.generate()

        tc = PkgConfigDeps(self)
        tc.generate()

    @staticmethod
    def _chmod_plus_x(name):
        os.chmod(name, os.stat(name).st_mode | 0o111)

    def _patch_sources(self):
        # Add missing wrapper scripts to the vendored meson
        save(self, self._meson_root.joinpath("meson"),
             textwrap.dedent("""\
                 #!/usr/bin/env bash
                 meson_dir=$(dirname "$0")
                 export PYTHONDONTWRITEBYTECODE=1
                 exec "$meson_dir/meson.py" "$@"
            """))
        self._chmod_plus_x(self._meson_root.joinpath("meson"))
        save(self, self._meson_root.joinpath("meson.cmd"),
             textwrap.dedent("""\
                 @echo off
                 set PYTHONDONTWRITEBYTECODE=1
                 CALL python %~dp0/meson.py %*
             """))

        # Install cython
        self.run(f"python -m pip install cython --no-cache-dir --target {self._build_site_packages}")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE*.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

    @property
    def _rel_site_packages(self):
        if self.settings.os == "Windows":
            return os.path.join("Lib", "site-packages")
        else:
            python_minor = Version(self.dependencies["cpython"].ref.version).minor
            return os.path.join("lib", f"python3.{python_minor}", "site-packages")

    @property
    def _rel_pkg_root(self):
        return os.path.join(self._rel_site_packages, "numpy")

    def package_info(self):
        self.cpp_info.components["npymath"].set_property("pkg_config_name", "npymath")
        self.cpp_info.components["npymath"].libs = ["npymath"]
        self.cpp_info.components["npymath"].libdirs = [
            os.path.join(self._rel_pkg_root, "core", "lib"),
            os.path.join(self._rel_pkg_root, "random", "lib"),
        ]
        self.cpp_info.components["npymath"].includedirs = [os.path.join(self._rel_pkg_root, "core", "include")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["npymath"].system_libs = ["m"]

        self.cpp_info.components["numpy"].libdirs = [os.path.join(self._rel_pkg_root, "core")]
        self.cpp_info.components["numpy"].requires = ["openblas::openblas", "cpython::cpython", "npymath"]
        self.cpp_info.components["numpy"].includedirs = []

        self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, self._rel_site_packages))
