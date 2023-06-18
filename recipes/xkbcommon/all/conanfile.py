import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.53.0"


class XkbcommonConan(ConanFile):
    name = "xkbcommon"
    package_type = "library"
    description = "keymap handling library for toolkits and window systems"
    topics = ("keyboard", "wayland", "x11", "xkb")
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
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("xkeyboard-config/system")
        if self.options.with_x11:
            self.requires("xorg/system")
        if self.options.get_safe("xkbregistry"):
            self.requires("libxml2/2.11.4")
        if self.options.get_safe("with_wayland"):
            self.requires("wayland/1.21.0")
            if not self._has_build_profile:
                self.requires("wayland-protocols/1.31")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration(f"{self.ref} is only compatible with Linux and FreeBSD")

    def build_requirements(self):
        self.tool_requires("meson/1.1.0")
        self.tool_requires("bison/3.8.2")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        if self._has_build_profile and self.options.get_safe("with_wayland"):
            self.tool_requires("wayland/1.21.0")
            self.tool_requires("wayland-protocols/1.31")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = MesonToolchain(self)
        tc.project_options["enable-docs"] = False
        tc.project_options["enable-wayland"] = self.options.get_safe("with_wayland", False)
        tc.project_options["enable-x11"] = self.options.with_x11
        if self._has_xkbregistry_option:
            tc.project_options["enable-xkbregistry"] = self.options.xkbregistry
        if self._has_build_profile:
            tc.project_options["build.pkg_config_path"] = self.generators_folder
        tc.generate()

        pkg_config_deps = PkgConfigDeps(self)
        if self._has_build_profile and self.options.get_safe("with_wayland"):
            pkg_config_deps.build_context_activated = ["wayland", "wayland-protocols"]
            pkg_config_deps.build_context_suffix = {"wayland": "_BUILD", "wayland-protocols": "_BUILD"}
        pkg_config_deps.generate()

    def build(self):
        if self.options.get_safe("with_wayland"):
            meson_build_file = os.path.join(self.source_folder, "meson.build")
            # Patch the build system to use the pkg-config files generated for the build context.

            if Version(self.version) >= "1.5.0":
                get_pkg_config_var = "get_variable(pkgconfig: "
            else:
                get_pkg_config_var = "get_pkgconfig_variable("

            if self._has_build_profile:
                replace_in_file(self, meson_build_file,
                                "wayland_scanner_dep = dependency('wayland-scanner', required: false, native: true)",
                                "wayland_scanner_dep = dependency('wayland-scanner_BUILD', required: false, native: true)")
                replace_in_file(self, meson_build_file,
                                "wayland_protocols_dep = dependency('wayland-protocols', version: '>=1.12', required: false)",
                                "wayland_protocols_dep = dependency('wayland-protocols_BUILD', version: '>=1.12', required: false, native: true)")
            else:
                replace_in_file(self, meson_build_file,
                                "wayland_scanner_dep = dependency('wayland-scanner', required: false, native: true)",
                                "# wayland_scanner_dep = dependency('wayland-scanner', required: false, native: true)")

                replace_in_file(self, meson_build_file,
                                "if not wayland_client_dep.found() or not wayland_protocols_dep.found() or not wayland_scanner_dep.found()",
                                "if not wayland_client_dep.found() or not wayland_protocols_dep.found()")

                replace_in_file(self, meson_build_file,
                                f"wayland_scanner = find_program(wayland_scanner_dep.{get_pkg_config_var}'wayland_scanner'))",
                                "wayland_scanner = find_program('wayland-scanner')")

        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

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
