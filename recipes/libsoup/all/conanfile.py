from conan import ConanFile
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.apple import fix_apple_shared_install_name
import os


required_conan_version = ">=2.4"


class LibSoup(ConanFile):
    name = "libsoup"
    description = "HTTP client/server library for GNOME"
    topics = "http", "networking", "glib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libsoup.gnome.org/"
    license = "LGPL-2.0-or-later"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    languages = "C"
    implements = ["auto_shared_fpic"]

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # INFO: Transitive headers libsoup/soup-types.h:9: gio/gio.h
        self.requires("glib/[>=2.78 <3]", transitive_headers=True)
        self.requires("libnghttp2/[>=1.59.0 <2]")
        self.requires("libpsl/[>=0.21.5 <1]")
        self.requires("sqlite3/[>=3.45.0 <4]")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        # INFO: Requires glib-mkenums to build soup-enum-types.h from soup-enum-types.h.template
        self.tool_requires("glib/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["gssapi"] = "disabled"
        tc.project_options["ntlm"] = "disabled"
        tc.project_options["brotli"] = "disabled"
        tc.project_options["tls_check"] = False
        tc.project_options["introspection"] = "disabled"
        tc.project_options["vapi"] = "disabled"
        tc.project_options["docs"] = "disabled"
        tc.project_options["doc_tests"] = False
        tc.project_options["tests"] = False
        tc.project_options["autobahn"] = "disabled"
        tc.project_options["installed_tests"] = False
        tc.project_options["sysprof"] = "disabled"
        tc.project_options["pkcs11_tests"] = "disabled"
        tc.generate()

        tc = PkgConfigDeps(self)
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["soup-3.0"]
        self.cpp_info.includedirs = ["include", "include/libsoup-3.0"]
        self.cpp_info.set_property("pkg_config_name", "libsoup-3.0")
