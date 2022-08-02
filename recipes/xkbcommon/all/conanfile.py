import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, replace_in_file, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version

required_conan_version = ">=1.47.0"


class XkbcommonConan(ConanFile):
    name = "xkbcommon"
    description = "keymap handling library for toolkits and window systems"
    topics = ("xkbcommon", "keyboard")
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

    generators = "PkgConfigDeps", "VirtualBuildEnv", "VirtualRunEnv"

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This library is only compatible with Linux or FreeBSD")

    def config_options(self):
        if not self._has_xkbregistry_option:
            del self.options.xkbregistry
        if self.settings.os != "Linux":
            del self.options.with_wayland

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("xorg/system")
        if self.options.get_safe("xkbregistry"):
            self.requires("libxml2/2.9.14")
        if self.options.get_safe("with_wayland"):
            self.requires("wayland/1.21.0")
            self.requires("wayland-protocols/1.26")  # FIXME: This should be a build-requires

    def build_requirements(self):
        self.tool_requires("meson/0.63.0")
        self.tool_requires("bison/3.7.6")
        self.tool_requires("pkgconf/1.7.4")
        if hasattr(self, "settings_build") and self.options.get_safe("with_wayland"):
            self.tool_requires("wayland/1.21.0")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        # Conan doesn't provide a `wayland-scanner.pc` file for the package in the _build_ context
        replace_in_file(
            self,
            os.path.join(self.source_folder, "meson.build"),
            "wayland_scanner_dep = dependency('wayland-scanner', required: false, native: true)",
            "# wayland_scanner_dep = dependency('wayland-scanner', required: false, native: true)")

        replace_in_file(
            self,
            os.path.join(self.source_folder, "meson.build"),
            "if not wayland_client_dep.found() or not wayland_protocols_dep.found() or not wayland_scanner_dep.found()",
            "if not wayland_client_dep.found() or not wayland_protocols_dep.found()")

        replace_in_file(
            self,
            os.path.join(self.source_folder, "meson.build"),
            "wayland_scanner = find_program(wayland_scanner_dep.get_pkgconfig_variable('wayland_scanner'))",
            "wayland_scanner = find_program('wayland-scanner')")

    @property
    def _has_xkbregistry_option(self):
        return Version(self.version) >= "1.0.0"

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["libdir"] = "lib"
        tc.project_options["default_library"] = "shared" if self.options.shared else "static"
        tc.project_options["enable-wayland"] = self.options.get_safe("with_wayland", False)
        tc.project_options["enable-docs"] = False
        tc.project_options["enable-x11"] = self.options.with_x11

        # workaround for https://github.com/conan-io/conan-center-index/issues/3377
        # FIXME: do not remove this pkg-config file once xorg recipe fixed
        xeyboard_config_pkgfile = os.path.join(self.build_folder, "xkeyboard-config.pc")
        if os.path.isfile(xeyboard_config_pkgfile):
            os.remove(xeyboard_config_pkgfile)

        if self._has_xkbregistry_option:
            tc.project_options["enable-xkbregistry"] = self.options.xkbregistry

        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_folder)
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["libxkbcommon"].set_property("pkg_config_name", "xkbcommon")
        self.cpp_info.components["libxkbcommon"].libs = ["xkbcommon"]
        self.cpp_info.components["libxkbcommon"].requires = ["xorg::xkeyboard-config"]
        if self.options.with_x11:
            self.cpp_info.components["libxkbcommon-x11"].set_property("pkg_config_name", "xkbcommon-x11")
            self.cpp_info.components["libxkbcommon-x11"].libs = ["xkbcommon-x11"]
            self.cpp_info.components["libxkbcommon-x11"].requires = ["libxkbcommon", "xorg::xcb", "xorg::xcb-xkb"]
        if self.options.get_safe("xkbregistry"):
            self.cpp_info.components["libxkbregistry"].set_property("pkg_config_name", "xkbregistry")
            self.cpp_info.components["libxkbregistry"].libs = ["xkbregistry"]
            self.cpp_info.components["libxkbregistry"].requires = ["libxml2::libxml2"]
        if self.options.get_safe("with_wayland", False):
            # FIXME: This generates just executable, but I need to use the requirements to pass Conan checks
            self.cpp_info.components["xkbcli-interactive-wayland"].libs = []
            self.cpp_info.components["xkbcli-interactive-wayland"].requires = ["wayland::wayland", "wayland-protocols::wayland-protocols"]

        if Version(self.version) >= "1.0.0":
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        # unofficial, but required to avoid side effects (libxkbcommon component
        # "steals" the default global pkg_config name)
        self.cpp_info.set_property("pkg_config_name", "xkbcommon_all_do_not_use")
        self.cpp_info.names["pkg_config"] = "xkbcommon_all_do_not_use"
