import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version

required_conan_version = ">=2.4"


class libdecorConan(ConanFile):
    name = "libdecor"
    description = "libdecor is a library that can help Wayland clients draw window decorations for them."
    topics = ("decoration", "wayland", "window")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/libdecor/libdecor"
    license = "MIT"

    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_dbus": [True, False],
        "with_gtk": [True, False],
    }
    default_options = {
        "with_dbus": True,
        # with_gtk is defaulted to false for CCI and missing binaries for version 3 of the gtk/system package.
        "with_gtk": False,
    }

    implements = ["auto_shared_fpic"]
    languages = "C"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cairo/1.18.0")
        if self.options.get_safe("with_dbus"):
            self.requires("dbus/1.15.8")
        if self.options.get_safe("with_gtk"):
            self.requires("gtk/system", options={"version": "3"})
        # Linking the test package results in missing freetype symbols without this.
        # It appears that this is due to an issue with a dependency such as pango or cairo pulling in the system freetype instead of Conan's.
        # Or potentially, it's related to an incorrectly specified dependency.
        self.requires("pango/1.51.0", transitive_libs=True)
        self.requires("wayland/1.22.0", transitive_headers=True)

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")
        if not self.dependencies["pango"].options.with_cairo:
            raise ConanInvalidConfiguration(f"{self.ref} requires the with_cairo option of pango to be enabled")
        if self.options.get_safe("with_gtk") and Version(self.dependencies["gtk"].options.version) < 3:
            raise ConanInvalidConfiguration(f"{self.ref} requires at least version 3 of GTK when the with_gtk option is enabled")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("wayland/<host_version>")
        self.tool_requires("wayland-protocols/1.33")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def _patch_sources(self):
        apply_conandata_patches(self)
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
        pkg_config_deps.build_context_activated = ["wayland-protocols"]
        pkg_config_deps.generate()

    def build(self):
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

        self.cpp_info.includedirs = [os.path.join("include", f"libdecor-{libdecor_soversion}")]

        plugins_soversion = "1"
        self.runenv_info.define("LIBDECOR_PLUGIN_DIR", os.path.join(self.package_folder, "lib", "libdecor", f"plugins-{plugins_soversion}"))
