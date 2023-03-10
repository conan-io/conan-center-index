from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import can_run
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os

required_conan_version = ">=1.53.0"


class LibsecretConan(ConanFile):
    name = "libsecret"
    description = "A library for storing and retrieving passwords and other secrets"
    topics = ("gobject", "password", "secret")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://wiki.gnome.org/Projects/Libsecret"
    license = "LGPL-2.1-or-later"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libgcrypt": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libgcrypt": True,
    }

    @property
    def _use_gcrypt(self):
        return self.options.get_safe("with_libgcrypt", False)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            # libgcrypt recipe is currently only available on Linux
            del self.options.with_libgcrypt

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/2.76.0", transitive_headers=True, transitive_libs=True, run=can_run(self))
        if self._use_gcrypt:
            self.requires("libgcrypt/1.8.4")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "libsecret recipe is not yet compatible with Windows."
            )

    def build_requirements(self):
        self.tool_requires("meson/1.0.0")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        if not can_run(self):
            self.tool_requires("glib/2.76.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if can_run(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = MesonToolchain(self)
        tc.project_options["introspection"] = "false"
        tc.project_options["manpage"] = "false"
        tc.project_options["gtk_doc"] = "false"
        tc.project_options["gcrypt"] = "true" if self._use_gcrypt else "false"
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libsecret-1")
        self.cpp_info.requires = ["glib::glib-2.0", "glib::gobject-2.0"]
        if self._use_gcrypt:
            self.cpp_info.requires.append("libgcrypt::libgcrypt")
        self.cpp_info.includedirs = [os.path.join("include", "libsecret-1")]
        self.cpp_info.libs = ["secret-1"]
