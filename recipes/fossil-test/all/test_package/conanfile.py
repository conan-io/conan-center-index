from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.meson import Meson, meson_layout
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "MesonToolchain", "PkgConfigDeps"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        meson_layout(self)

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
