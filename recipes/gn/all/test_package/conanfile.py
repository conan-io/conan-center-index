import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run, cross_building
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VCVars"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        self.tool_requires("ninja/1.11.1")

    def layout(self):
        basic_layout(self)

    @property
    def _target_os(self):
        if is_apple_os(self):
            return "mac"
        # Assume gn knows about the os
        return {
            "Windows": "win",
        }.get(str(self.settings.os), str(self.settings.os).lower())

    @property
    def _target_cpu(self):
        return {
            "x86_64": "x64",
        }.get(str(self.settings.arch), str(self.settings.arch))

    def generate(self):
        VirtualBuildEnv(self).generate()
        VirtualRunEnv(self).generate(scope="run")
        VirtualRunEnv(self).generate(scope="build")

    def build(self):
        if not cross_building(self):
            rel_bindir = unix_path(self, os.path.relpath(os.path.join(self.cpp.build.bindir), os.getcwd()))
            gn_args = [
                rel_bindir,
                f'--args="target_os=\\"{self._target_os}\\" target_cpu=\\"{self._target_cpu}\\""',
            ]
            self.run("gn gen " + " ".join(gn_args))
            self.run(f"ninja -v -j{os.cpu_count()} -C {rel_bindir}")

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
