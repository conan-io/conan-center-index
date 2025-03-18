import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.0.5"


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
    implements = ["auto_shared_fpic"]
    languages = ["C"]

    @property
    def _has_xkbregistry_option(self):
        return Version(self.version) >= "1.0.0"

    def config_options(self):
        if not self._has_xkbregistry_option:
            del self.options.xkbregistry
        if self.settings.os not in ("Linux", "Android"):
            del self.options.with_wayland
        if self.settings.os == "Android":
            del self.options.with_x11

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("xkeyboard-config/system")
        if self.options.get_safe("with_x11"):
            self.requires("xorg/system")
        if self.options.get_safe("xkbregistry"):
            self.requires("libxml2/[>=2.12.5 <3]")
        if self.options.get_safe("with_wayland"):
            self.requires("wayland/1.22.0")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD", "Android"]:
            raise ConanInvalidConfiguration(f"{self.ref} is only compatible with Linux, FreeBSD and Android")

    def build_requirements(self):
        self.tool_requires("meson/1.3.2")
        self.tool_requires("bison/3.8.2")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        if self.options.get_safe("with_wayland"):
            self.tool_requires("wayland/<host_version>")
            self.tool_requires("wayland-protocols/1.33")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        if Version(self.version) >= "1.6":
            tc.project_options["enable-bash-completion"] = False
        tc.project_options["enable-docs"] = False
        tc.project_options["enable-wayland"] = self.options.get_safe("with_wayland", False)
        tc.project_options["enable-x11"] = self.options.get_safe("with_x11", False)
        if self._has_xkbregistry_option:
            tc.project_options["enable-xkbregistry"] = self.options.xkbregistry
        tc.project_options["build.pkg_config_path"] = self.generators_folder
        if self.settings.os == "Android":
            tc.project_options["enable-tools"] = False
        tc.generate()

        pkg_config_deps = PkgConfigDeps(self)
        if self.options.get_safe("with_wayland"):
            pkg_config_deps.build_context_activated = ["wayland", "wayland-protocols"]
            pkg_config_deps.build_context_suffix = {"wayland": "_BUILD"}
        pkg_config_deps.generate()

    def _patch_sources(self):
        if self.options.get_safe("with_wayland"):
            # Patch the build system to use the pkg-config files generated for the build context.
            meson_build_file = os.path.join(self.source_folder, "meson.build")
            replace_in_file(
                self,
                meson_build_file,
                "wayland_scanner_dep = dependency('wayland-scanner', required: false, native: true)",
                "wayland_scanner_dep = dependency('wayland-scanner_BUILD', required: false, native: true)",
            )

    def build(self):
        self._patch_sources()
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

        if self.options.get_safe("with_x11"):
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

        # unofficial, but required to avoid side effects (libxkbcommon component
        # "steals" the default global pkg_config name)
        self.cpp_info.set_property("pkg_config_name", "xkbcommon_all_do_not_use")
