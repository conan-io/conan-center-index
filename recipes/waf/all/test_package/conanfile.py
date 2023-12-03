import os
import shutil

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import chdir
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"
    exports_sources = "a.cpp", "b.cpp", "main.c", "main.cpp", "wscript"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def generate(self):
        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

        env = Environment()
        for var in ["DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"]:
            env.append_path(var, self.build_folder)
        env.vars(self, scope="run").save_script("conanrun_macos_dyld_path")

    def build(self):
        if can_run(self):
            for src in self.exports_sources:
                shutil.copy(os.path.join(self.source_folder, src), self.build_folder)

            with chdir(self, self.build_folder):
                self.run(f"waf configure -o {self.cpp.build.bindir}")
                self.run("waf")

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "app")
            self.run(bin_path, env="conanrun")
            bin_path = os.path.join(self.cpp.build.bindir, "app2")
            self.run(bin_path, env="conanrun")
