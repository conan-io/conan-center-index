import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, save
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain

required_conan_version = ">=1.53.0"


class CageConan(ConanFile):
    name = "cage"
    description = "Cage is a kiosk compositor for Wayland."
    topics = ("compositor", "display", "kiosk", "wayland")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.hjdskes.nl/projects/cage/"
    license = "MIT"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "xwayland": [True, False],
    }
    default_options = {
        "xwayland": False,
    }

    @property
    def _has_build_profile(self):
        return hasattr(self, "settings_build")

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        self.options["wlroots"].xwayland = self.options.xwayland
        self.options["xkbcommon"].with_wayland = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("pixman/0.43.0")
        self.requires("wayland/1.22.0")
        self.requires("wlroots/0.17.1")
        self.requires("xkbcommon/1.6.0")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")
        if self.options.xwayland and not self.dependencies["wlroots"].options.xwayland:
            raise ConanInvalidConfiguration(
                "The xwayland option requires the wlroots xwayland option to be enabled"
            )

    def build_requirements(self):
        self.tool_requires("meson/1.3.2")
        self.tool_requires("wayland/<host_version>")
        self.tool_requires("wayland-protocols/1.33")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["xwayland"] = "enabled" if self.options.xwayland else "disabled"
        tc.project_options["man-pages"] = "disabled"
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
            save(
                self,
                os.path.join(self.generators_folder, "wayland-protocols.pc"),
                wp_pkg_content,
            )
        pkg_config_deps.generate()
        env = VirtualBuildEnv(self)
        env.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.system_libs = ["m"]
