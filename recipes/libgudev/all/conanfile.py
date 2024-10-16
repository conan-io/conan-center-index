import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain


required_conan_version = ">=1.53.0"


class LibgudevConan(ConanFile):
    name = "libgudev"
    description = "This is libgudev, a library providing GObject bindings for libudev."
    license = "LGPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/libgudev/"
    topics = ("device", "gobject", "udev")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "introspection": [True, False],
        "with_libudev": ["eudev", "systemd"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        # Introspection is disabled by default since gobject-introspection is not Conan V2 ready.
        "introspection": False,
        # Default to eudev for CCI which doesn't have a new enough version of libudev from the libudev/system package.
        "with_libudev": "eudev",
    }

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/2.78.3")
        if self.options.with_libudev == "eudev":
            self.requires("eudev/3.2.14")
        elif self.options.with_libudev == "systemd":
            self.requires("libudev/system")

    def validate(self):
        if self.settings.os not in ["FreeBSD", "Linux"]:
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support {self.settings.os}."
            )

    def build_requirements(self):
        self.tool_requires("meson/1.3.2")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        self.tool_requires("glib/<host_version>")
        if self.options.introspection:
            self.tool_requires("gobject-introspection/1.72.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["gtk_doc"] = False
        tc.project_options["introspection"] = (
            "enabled" if self.options.introspection else "disabled"
        )
        tc.project_options["tests"] = "disabled"
        tc.project_options["vapi"] = "disabled"
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(
            self,
            "COPYING",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["gudev-1.0"]
        self.cpp_info.includedirs = [
            os.path.join(self.package_folder, "include", "gudev-1.0")
        ]
        self.cpp_info.requires = [
            "glib::glib-2.0",
            "glib::gobject-2.0",
        ]
        if self.options.with_libudev == "eudev":
            self.cpp_info.requires.append("eudev::eudev")
        elif self.options.with_libudev == "systemd":
            self.cpp_info.requires.append("libudev::libudev")
        self.cpp_info.set_property("pkg_config_name", "gudev-1.0")
