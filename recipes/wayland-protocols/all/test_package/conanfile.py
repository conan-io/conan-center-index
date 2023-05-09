from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    test_type = "explicit"

    @property
    def _has_build_profile(self):
        return hasattr(self, "settings_build")

    def requirements(self):
        self.requires(self.tested_reference_str)
        self.requires("wayland/1.21.0")

    def build_requirements(self):
        self.tool_requires("meson/1.1.0")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        self.tool_requires("wayland/1.21.0")

    def layout(self):
        basic_layout(self)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["build.pkg_config_path"] = self.generators_folder
        tc.project_options["has_build_profile"] = self._has_build_profile
        tc.generate()
        pkg_config_deps = PkgConfigDeps(self)
        if self._has_build_profile:
            pkg_config_deps.build_context_activated = ["wayland"]
            pkg_config_deps.build_context_suffix = {"wayland": "_BUILD"}
        pkg_config_deps.generate()
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def test(self):
        if can_run(self):
            cmd = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(cmd, env="conanrun")
