import os
from conan import ConanFile
from conans import Meson
from conan.tools.build import cross_building


class LibniceTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"
        
    def build_requirements(self):
        self.tool_requires("meson/0.64.1")
        self.tool_requires("pkgconf/1.9.3")
        self.tool_requires("meson/0.64.1")

    def build(self):
        meson = Meson(self)
        meson.configure(build_folder="bin", source_folder="../test_package")
        meson.build()

    def test(self):
        if not cross_building(self, skip_x64_x86=True):
            cmd = os.path.join("bin", "example")
            self.run(cmd, run_environment=True)
