import os
import textwrap

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, save
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
    def _has_build_profile(self):
        return hasattr(self, "settings_build")

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        self.options["pango"].with_cairo = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cairo/1.18.0")
        if self.options.get_safe("with_dbus"):
            self.requires("dbus/1.15.8")
        if self.options.get_safe("with_gtk"):
            self.requires("gtk/system")
        # Linking the test package results in missing freetype sympols without this.
        # It appears that this is due to an issue with a dependency such as pango or cairo pulling in the system freetype instead of Conan's.
        # Or potentially, it's related to an incorrectly specified dependency.
        self.requires("pango/1.51.0", transitive_libs=True)
        self.requires("wayland/1.22.0", transitive_headers=True)

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")
        if not self.dependencies["pango"].options.with_cairo:
            raise ConanInvalidConfiguration(f"{self.ref} requires the with_cairo option of pango to be enabled")

    def build_requirements(self):
        self.tool_requires("meson/1.3.2")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        self.tool_requires("wayland/<host_version>")
        self.tool_requires("wayland-protocols/1.33")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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
        if self._has_build_profile:
            pkg_config_deps.build_context_activated = ["wayland-protocols"]
        else:
            # Manually generate pkgconfig file of wayland-protocols since
            # PkgConfigDeps.build_context_activated can't work with legacy 1 profile
            # We must use legacy conan v1 deps_cpp_info because self.dependencies doesn't
            # contain build requirements when using 1 profile.
            wp_prefix = self.deps_cpp_info["wayland-protocols"].rootpath
            wp_version = self.deps_cpp_info["wayland-protocols"].version
            wp_pkg_content = textwrap.dedent(f"""\
                prefix={wp_prefix}
                datarootdir=${{prefix}}/res
                pkgdatadir=${{datarootdir}}/wayland-protocols
                Name: Wayland Protocols
                Description: Wayland protocol files
                Version: {wp_version}
            """)
            save(self, os.path.join(self.generators_folder, "wayland-protocols.pc"), wp_pkg_content)
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
