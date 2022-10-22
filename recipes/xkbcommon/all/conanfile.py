import glob
import os
import shutil

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, mkdir, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.52.0"


class XkbcommonConan(ConanFile):
    name = "xkbcommon"
    description = "keymap handling library for toolkits and window systems"
    topics = ("keyboard")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xkbcommon/libxkbcommon"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_x11": [True, False],
        "with_wayland": [True, False],
        "xkbregistry": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_x11": True,
        "with_wayland": True,
        "xkbregistry": True,
    }

    @property
    def _has_build_profile(self):
        return hasattr(self, "settings_build")

    @property
    def _has_xkbregistry_option(self):
        return Version(self.version) >= "1.0.0"

    def config_options(self):
        if not self._has_xkbregistry_option:
            del self.options.xkbregistry
        if self.settings.os != "Linux":
            del self.options.with_wayland

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def requirements(self):
        self.requires("xkeyboard-config/system")
        if self.options.with_x11:
            self.requires("xorg/system")
        if self.options.get_safe("xkbregistry"):
            self.requires("libxml2/2.9.14")
        if self.options.get_safe("with_wayland"):
            self.requires("wayland/1.21.0")
            if not self._has_build_profile:
                self.requires("wayland-protocols/1.27")

    def validate(self):
        if self.info.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration(f"{self.ref} is only compatible with Linux and FreeBSD")

    def build_requirements(self):
        self.tool_requires("meson/0.63.3")
        self.tool_requires("bison/3.8.2")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        if self._has_build_profile and self.options.get_safe("with_wayland"):
            self.tool_requires("wayland/1.21.0")
            self.tool_requires("wayland-protocols/1.27")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["enable-docs"] = False
        tc.project_options["enable-wayland"] = self.options.get_safe("with_wayland", False)
        tc.project_options["enable-x11"] = self.options.with_x11
        if self._has_xkbregistry_option:
            tc.project_options["enable-xkbregistry"] = self.options.xkbregistry
        if self._has_build_profile:
            tc.project_options["build.pkg_config_path"] = os.path.join(self.generators_folder, "build")
        tc.generate()

        pkg_config_deps = PkgConfigDeps(self)
        if self._has_build_profile and self.options.get_safe("with_wayland"):
            pkg_config_deps.build_context_activated = ["wayland", "wayland-protocols"]
            pkg_config_deps.build_context_suffix = {"wayland": "_BUILD"}
        pkg_config_deps.generate()
        if self._has_build_profile and self.options.get_safe("with_wayland"):
            mkdir(self, os.path.join(self.generators_folder, "build"))
            for pc in glob.glob(os.path.join(self.generators_folder, "*_BUILD.pc")):
                original_pc = os.path.basename(pc)[:-9] + ".pc"
                shutil.move(pc, os.path.join(self.generators_folder, "build", original_pc))

        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()

    def build(self):
        # Conan doesn't provide a `wayland-scanner.pc` file for the package in the _build_ context
        if self.options.get_safe("with_wayland") and not self._has_build_profile:
            meson_build_file = os.path.join(self.source_folder, "meson.build")
            replace_in_file(self, meson_build_file,
                            "wayland_scanner_dep = dependency('wayland-scanner', required: false, native: true)",
                            "# wayland_scanner_dep = dependency('wayland-scanner', required: false, native: true)")

            replace_in_file(self, meson_build_file,
                            "if not wayland_client_dep.found() or not wayland_protocols_dep.found() or not wayland_scanner_dep.found()",
                            "if not wayland_client_dep.found() or not wayland_protocols_dep.found()")

            replace_in_file(self, meson_build_file,
                            "wayland_scanner = find_program(wayland_scanner_dep.get_pkgconfig_variable('wayland_scanner'))",
                            "wayland_scanner = find_program('wayland-scanner')")

        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        fix_apple_shared_install_name(self)
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["libxkbcommon"].set_property("pkg_config_name", "xkbcommon")
        self.cpp_info.components["libxkbcommon"].libs = ["xkbcommon"]
        self.cpp_info.components["libxkbcommon"].requires = ["xkeyboard-config::xkeyboard-config"]
        self.cpp_info.components["libxkbcommon"].resdirs = ["res"]

        if self.options.with_x11:
            self.cpp_info.components["libxkbcommon-x11"].set_property("pkg_config_name", "xkbcommon-x11")
            self.cpp_info.components["libxkbcommon-x11"].libs = ["xkbcommon-x11"]
            self.cpp_info.components["libxkbcommon-x11"].requires = ["libxkbcommon", "xorg::xcb", "xorg::xcb-xkb"]
        if self.options.get_safe("xkbregistry"):
            self.cpp_info.components["libxkbregistry"].set_property("pkg_config_name", "xkbregistry")
            self.cpp_info.components["libxkbregistry"].libs = ["xkbregistry"]
            self.cpp_info.components["libxkbregistry"].requires = ["libxml2::libxml2"]
        if self.options.get_safe("with_wayland", False):
            self.cpp_info.components["xkbcli-interactive-wayland"].libs = []
            self.cpp_info.components["xkbcli-interactive-wayland"].includedirs = []
            self.cpp_info.components["xkbcli-interactive-wayland"].requires = ["wayland::wayland-client"]
            if not self._has_build_profile:
                self.cpp_info.components["xkbcli-interactive-wayland"].requires.append("wayland-protocols::wayland-protocols")

        if Version(self.version) >= "1.0.0":
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bindir}")
            self.env_info.PATH.append(bindir)

        # unofficial, but required to avoid side effects (libxkbcommon component
        # "steals" the default global pkg_config name)
        self.cpp_info.set_property("pkg_config_name", "xkbcommon_all_do_not_use")
        self.cpp_info.names["pkg_config"] = "xkbcommon_all_do_not_use"
