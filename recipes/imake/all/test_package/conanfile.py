from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.gnu import Autotools, AutotoolsToolchain


required_conan_version = ">=1.54.0"


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

        if not self.conf.get("tools.gnu:make_program", check_type=str):
            self.tool_requires("make/4.3")

    def layout(self):
        basic_layout(self)

    def generate(self):
        tc = AutotoolsToolchain(self)

        env = tc.environment()
        if is_msvc(self):
            env.define("CC", "cl -nologo")
        tc.generate(env)

        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

    def build(self):
        copy(self, "Imake*", self.source_folder, self.build_folder)
        self.run("imake", env="conanbuild")
        autotools = Autotools(self)
        autotools.make()

    def test(self):
        # test is successful if we can invoke make in the build step
        pass