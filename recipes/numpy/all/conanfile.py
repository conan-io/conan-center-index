import os
import textwrap

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import copy, export_conandata_patches, get, apply_conandata_patches, rmdir, move_folder_contents, mkdir, save
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
    homepage = "https://numpy.org/doc/stable/reference/c-api/coremath.html"
    topics = ("ndarray", "array", "linear algebra", "npymath", "npyrandom")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openblas/0.3.26")
        self.requires("cpython/3.10.0", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("cpython/<host_version>")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _meson_root(self):
        return self.source_path.joinpath("vendored-meson", "meson")

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        # NumPy can only be built with its vendored Meson
        env = Environment()
        env.prepend_path("PATH", str(self._meson_root))
        env.vars(self).save_script("conanbuild_meson")

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
        apply_conandata_patches(self)
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

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE*.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        python_minor = Version(self.dependencies["cpython"].ref.version).minor
        python_lib = os.path.join(self.package_folder, "lib", f"python3.{python_minor}")
        pkg_root = os.path.join(python_lib, "site-packages", "numpy")
        copy(self, "*.a", pkg_root, os.path.join(self.package_folder, "lib"), keep_path=False)
        mkdir(self, os.path.join(self.package_folder, "include"))
        move_folder_contents(self, os.path.join(pkg_root, "core", "include"), os.path.join(self.package_folder, "include"))
        rmdir(self, python_lib)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.components["npymath"].set_property("pkg_config_name", "npymath")
        self.cpp_info.components["npymath"].libs = ["npymath", "npyrandom"]
        self.cpp_info.components["npymath"].requires = ["openblas::openblas", "cpython::cpython"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["npymath"].system_libs = ["m"]
