import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import Environment
from conan.tools.files import copy, export_conandata_patches, get, apply_conandata_patches, rmdir, move_folder_contents, mkdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
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
        self.requires("openblas/0.3.20")
        self.requires("cpython/3.10.0", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # NumPy can only be built with its vendored Meson
        env = Environment()
        env.prepend_path("PATH", os.path.join(self.source_folder, "vendored-meson", "entrypoint"))
        env.vars(self).save_script("conanbuild_meson")
        tc = MesonToolchain(self)
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE*.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()
        python_minor = Version(self.dependencies["cpython"].ref.version).minor
        pkg_root = os.path.join(self.package_folder, "lib", f"python3.{python_minor}", "site-packages", "numpy")
        copy(self, "*.a", pkg_root, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        mkdir(self, os.path.join(self.package_folder, "include"))
        move_folder_contents(self, os.path.join(pkg_root, "core", "include"), os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "lib", f"python3.{python_minor}"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.components["npymath"].set_property("pkg_config_name", "npymath")
        self.cpp_info.components["npymath"].libs = ["npymath", "npyrandom"]
        self.cpp_info.components["npymath"].requires = [
            "openblas::openblas",
            "cpython::cpython"
        ]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["npymath"].system_libs = ["m"]
