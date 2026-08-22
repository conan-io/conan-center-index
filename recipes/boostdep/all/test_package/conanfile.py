from conan import ConanFile
from conan.tools.env import Environment
from conan.tools.files import mkdir, save


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        mkdir(self, "libs")
        save(self, "Jamroot", "")
        env = Environment()
        env.define("BOOST_ROOT", self.build_folder)
        with env.vars(self).apply():
            self.run("boostdep --list-modules")
