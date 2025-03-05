from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0.6"


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
        "crypto": [False, "libgcrypt", "gnutls"],
        "with_libgcrypt": [True, False, "deprecated"],
        "with_introspection": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "crypto": "libgcrypt",
        "with_libgcrypt": "deprecated",
        "with_introspection": False,
    }

    def config_options(self):
        if self.settings.os != "Linux":
            # libgcrypt recipe is currently only available on Linux
            self.options.crypto = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if self.options.with_libgcrypt != "deprecated":
            self.output.warning(f"The '{self.ref}:with_libgcrypt' option is deprecated. Use '{self.ref}:crypto' instead.")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("crypto") == "libgcrypt":
            self.requires("libgcrypt/1.10.3")
        elif self.options.get_safe("crypto") == "gnutls":
            self.requires("gnutls/3.8.2")
        if self.options.with_introspection:
            self.requires("gobject-introspection/1.78.1")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} recipe is not yet compatible with Windows.")
        if self.options.crypto == "gnutls" and Version(self.version) < "0.21.2":
            raise ConanInvalidConfiguration(f"{self.ref} does not support GnuTLS before version 0.21.2. Use -o '&:crypto=libgcrypt' instead.")

    def package_id(self):
        del self.info.options.with_libgcrypt

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("glib/<host_version>")
        self.tool_requires("gettext/0.22.5")
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = MesonToolchain(self)
        tc.project_options["introspection"] = "true" if self.options.with_introspection else "false"
        tc.project_options["vapi"] = "false"
        tc.project_options["manpage"] = "false"
        tc.project_options["gtk_doc"] = "false"
        if Version(self.version) >= "0.21.2":
            tc.project_options["crypto"] = str(self.options.crypto) if self.options.crypto else "disabled"
        else:
            tc.project_options["gcrypt"] = "true" if self.options.crypto == "libgcrypt" else "false"
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
        os.rename(os.path.join(self.package_folder, "share"),
                  os.path.join(self.package_folder, "res"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libsecret-1")
        self.cpp_info.includedirs = [os.path.join("include", "libsecret-1")]
        self.cpp_info.resdirs = ["res"]
        self.cpp_info.libs = ["secret-1"]
        self.cpp_info.requires = ["glib::glib-2.0", "glib::gobject-2.0", "glib::gio-2.0"]
        if self.options.get_safe("crypto") == "libgcrypt":
            self.cpp_info.requires.append("libgcrypt::libgcrypt")
        elif self.options.get_safe("crypto") == "gnutls":
            self.cpp_info.requires.append("gnutls::gnutls")
        if self.options.with_introspection:
            self.cpp_info.requires.append("gobject-introspection::gobject-introspection")
            self.buildenv_info.append_path("GI_GIR_PATH", os.path.join(self.package_folder, "res", "gir-1.0"))
            self.runenv_info.append_path("GI_TYPELIB_PATH", os.path.join(self.package_folder, "lib", "girepository-1.0"))
