import os
import shutil

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.53.0"


class libdecorConan(ConanFile):
    name = "libdecor"
    package_type = "shared-library"
    description = "libdecor is a library that can help Wayland clients draw window decorations for them."
    topics = ("decoration", "wayland", "window")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/libdecor/libdecor"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_dbus": [True, False],
        "with_gtk": [True, False],
    }
    default_options = {
        "with_dbus": True,
        "with_gtk": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if self.options.get_safe("with_gtk"):
            self.options["gtk"].version = "3"
        self.options["pango"].with_cairo = True

        # https://gitlab.freedesktop.org/libdecor/libdecor/-/issues/66
        if self.options.get_safe("wayland"):
            self.options["shared"].version = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cairo/1.18.0")
        if self.options.get_safe("with_dbus"):
            self.requires("dbus/1.15.8")
        if self.options.get_safe("with_gtk"):
            self.requires("gtk/system")
        self.requires("pango/1.51.0")
        self.requires("wayland/1.22.0")
        self.requires("wayland-protocols/1.32")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")
        if self.options.get_safe("with_gtk") and not self.dependencies["gtk"].options.version == "3":
            raise ConanInvalidConfiguration(f"{self.ref} requires the version option of gtk to be set to 3")
        if not self.dependencies["pango"].options.with_cairo:
            raise ConanInvalidConfiguration(f"{self.ref} requires the with_cairo option of pango to be enabled")

        # https://gitlab.freedesktop.org/libdecor/libdecor/-/issues/66
        if not self.dependencies["wayland"].options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} requires the shared option of wayland to be enabled due to a bug in libdecor")

    def build_requirements(self):
        self.tool_requires("meson/1.3.1")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        self.tool_requires("wayland/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        replace_in_file(
            self,
            os.path.join(self.source_folder, "src", "plugins", "meson.build"),
            "gtk_dep = dependency('gtk+-3.0', required: get_option('gtk'))",
            "gtk_dep = dependency('gtk', required: get_option('gtk'))",
        )

    def generate(self):
        def feature(option):
            return "enabled" if self.options.get_safe(option) else "disabled"

        tc = MesonToolchain(self)
        tc.project_options["dbus"] = feature("with_dbus")
        tc.project_options["demo"] = False
        tc.project_options["gtk"] = feature("with_gtk")
        tc.generate()
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        libdecor_soversion = "0"
        self.cpp_info.libs = [f"decor-{libdecor_soversion}"]
        self.cpp_info.set_property("pkg_config_name", f"libdecor-{libdecor_soversion}")

        self.cpp_info.includedirs = [os.path.join(self.package_folder, "include", f"libdecor-{libdecor_soversion}")]

        plugins_soversion = "1"
        self.runenv_info.define("LIBDECOR_PLUGIN_DIR", os.path.join(self.package_folder, "lib", "libdecor", f"plugins-{plugins_soversion}"))
