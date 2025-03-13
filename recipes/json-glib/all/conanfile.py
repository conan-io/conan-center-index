import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import get, rmdir, mkdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain

required_conan_version = ">=2.4"


class JsonGlibConan(ConanFile):
    name = "json-glib"
    description = "JSON-GLib implements a full JSON parser and generator using GLib and GObject, and integrates JSON with GLib data types."
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://wiki.gnome.org/Projects/JsonGlib"
    topics = ("json", "gobject")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_introspection": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_introspection": False,
    }
    languages = ["C"]
    implements = ["auto_shared_fpic"]

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/2.78.3", transitive_headers=True)
        if self.options.with_introspection:
            self.requires("gobject-introspection/1.78.1")

    def validate(self):
        if self.options.with_introspection and not self.options.shared:
            raise ConanInvalidConfiguration("with_introspection=True requires -o shared=True")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("glib/<host_version>")
        self.tool_requires("gettext/0.22.5")
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["tests"] = "false"
        tc.project_options["documentation"] = "disabled"
        tc.project_options["man"] = "false"
        tc.project_options["nls"] = "enabled"
        tc.project_options["introspection"] = "enabled" if self.options.with_introspection else "disabled"
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        # handle license file being a symlink
        mkdir(self, os.path.join(self.package_folder, "licenses"))
        shutil.copy2(os.path.join(self.source_folder, "COPYING"),
                     os.path.join(self.package_folder, "licenses", "COPYING"),
                     follow_symlinks=True)
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.rename(os.path.join(self.package_folder, "share"),
                  os.path.join(self.package_folder, "res"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "json-glib-1.0")
        self.cpp_info.libs = ["json-glib-1.0"]
        self.cpp_info.includedirs = [os.path.join("include", "json-glib-1.0")]
        self.cpp_info.requires = ["glib::gio-2.0"]
        self.cpp_info.resdirs = ["res"]
        if self.options.with_introspection:
            self.cpp_info.requires.append("gobject-introspection::gobject-introspection")
            self.buildenv_info.append_path("GI_GIR_PATH", os.path.join(self.package_folder, "res", "gir-1.0"))
            self.runenv_info.append_path("GI_TYPELIB_PATH", os.path.join(self.package_folder, "lib", "girepository-1.0"))
