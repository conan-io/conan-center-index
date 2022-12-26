import os
from conan import ConanFile
from conan.tools.meson import Meson
from conan.tools.layout import basic_layout
from conan.tools.build import cross_building


class LibniceTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "PkgConfigDeps", "MesonToolchain"
    apply_env = False

    def build_requirements(self):
        self.build_requires("meson/0.64.1")
        self.build_requires("pkgconf/1.9.3")

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def layout(self):
        basic_layout(self)

    def test(self):
        if not cross_building(self, skip_x64_x86=True):
            cmd = os.path.join(self.cpp.build.bindirs[0], "example")
            self.run(cmd, run_environment=True, env="conanrun")
