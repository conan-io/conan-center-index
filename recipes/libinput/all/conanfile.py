from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os


required_conan_version = ">=1.53.0"


class LibinputConan(ConanFile):
    name = "libinput"
    description = "libinput is a library that handles input devices for display servers and other applications that need to directly deal with input devices."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/libinput/"
    topics = ("device", "display", "event", "input")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "epoll_dir": [None, "ANY"],
        "debug_gui": [True, False],
        "with_libudev": ["eudev", "systemd"],
        "with_libwacom": [True, False],
        "with_wayland": [True, False],
        "with_x11": [True, False],
    }
    default_options = {
        "epoll_dir": None,
        "debug_gui": True,
        "with_libudev": "systemd",
        # todo Package libwacom and enable this option by default.
        "with_libwacom": False,
        "with_wayland": True,
        "with_x11": True,
    }

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if not self.options.debug_gui:
            self.options.rm_safe("with_wayland")
            self.options.rm_safe("with_x11")
        if self.options.get_safe("with_wayland"):
            self.options["gtk"].with_wayland = True
        if self.options.get_safe("with_x11"):
            self.options["gtk"].with_x11 = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("mtdev/1.1.6")
        self.requires("libevdev/1.13.1")

        if self.options.debug_gui:
            self.requires("cairo/1.17.6")
            self.requires("glib/2.78.0")
            self.requires("gtk/4.7.0")
            if self.options.with_wayland:
                self.requires("wayland/1.22.0")
                self.requires("wayland-protocols/1.31")
            if self.options.with_x11:
                self.requires("xorg/system")

        if self.options.with_libudev == "systemd":
            # todo Use libudev from the libsystemd package.
            # self.requires("libsystemd/253.10", transitive_libs=True)
            self.requires("libudev/system", transitive_libs=True)
        elif self.options.with_libudev == "eudev":
            self.requires("eudev/3.2.12", transitive_libs=True)

    def validate(self):
        if not self.settings.os in ["FreeBSD", "Linux"]:
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")
        if self.options.with_libwacom:
            raise ConanInvalidConfiguration(f"The with_libwacom option for {self.ref} is not yet supported. Contributions welcome.")

    def build_requirements(self):
        self.tool_requires("meson/1.2.2")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")
        if self.options.get_safe("with_wayland"):
            self.tool_requires("wayland/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["coverity"] = False
        tc.project_options["datadir"] = "res"
        tc.project_options["documentation"] = False
        tc.project_options["epoll-dir"] = '' if self.options.epoll_dir is None else str(self.options.epoll_dir)
        tc.project_options["debug-gui"] = self.options.debug_gui
        tc.project_options["install-tests"] = False
        # Change libexecdir so that the libinput subdirectory in the bin directory doesn't conflict with the libinput executable.
        tc.project_options["libexecdir"] = "libexec"
        tc.project_options["libwacom"] = self.options.with_libwacom
        tc.project_options["tests"] = False
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
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        copy(self, f"{self.name}-*", os.path.join(self.package_folder, "libexec", self.name), os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "libexec"))

        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "res", "zsh"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["input"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "rt"])
