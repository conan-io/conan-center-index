from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os

required_conan_version = ">=2.31"


class LibdecorConan(ConanFile):
    name = "libdecor"
    description = "Client-side window decoration library for Wayland clients"
    topics = ("wayland", "window-decoration")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/libdecor/libdecor"
    license = "MIT"
    package_type = "shared-library"
    languages = "C"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_dbus": [True, False],
        "with_gtk": [True, False],
    }
    default_options = {
        "with_dbus": True,
        "with_gtk": True,
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("wayland/[>=1.18 <2]", transitive_headers=True)
        self.requires("pango/[>=1.50.7 <2]")
        if self.options.with_dbus:
            self.requires("dbus/[>=1.14 <2]")
        if self.options.with_gtk:
            self.requires("gtk/[>=3.24 <4]", options={"with_wayland": True})

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        # INFO: wayland is required due to wayland-scanner build tool
        self.tool_requires("wayland/<host_version>")
        self.tool_requires("wayland-protocols/[>=1.15 <2]")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")
        if not self.dependencies["pango"].options.with_cairo:
            raise ConanInvalidConfiguration(f"{self.ref} requires pango/*:with_cairo=True")
        if self.options.with_gtk and not self.dependencies["gtk"].options.with_wayland:
            raise ConanInvalidConfiguration(
                f'{self.ref} requires GTK with Wayland support. Build it with -o "gtk/*:with_wayland=True"'
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        deps = PkgConfigDeps(self)
        deps.build_context_activated = ["wayland-protocols"]
        deps.generate()

        tc = MesonToolchain(self)
        tc.project_options["demo"] = False
        tc.project_options["install_demo"] = False
        tc.project_options["gtk"] = "enabled" if self.options.with_gtk else "disabled"
        tc.project_options["dbus"] = "enabled" if self.options.with_dbus else "disabled"
        tc.project_options["libdir"] = "lib"
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libdecor")
        self.cpp_info.set_property("cmake_target_name", "libdecor::libdecor")
        self.cpp_info.set_property("pkg_config_name", "libdecor-0")
        self.cpp_info.libs = ["decor-0"]
        self.cpp_info.includedirs = [os.path.join("include", "libdecor-0")]
        self.cpp_info.system_libs = ["dl"]
        self.cpp_info.requires = ["wayland::wayland-client"]

        # These dependencies are used internally by runtime-loaded decoration plugins and are not part of libdecor's consumer link interface.
        self.cpp_info.ignored_requires.append("pango")
        if self.options.with_dbus:
            self.cpp_info.ignored_requires.append("dbus")
        if self.options.with_gtk:
            self.cpp_info.ignored_requires.append("gtk")

        plugin_dir = os.path.join(self.package_folder, "lib", "libdecor", "plugins-1")
        self.runenv_info.prepend_path("LIBDECOR_PLUGIN_DIR", plugin_dir)
