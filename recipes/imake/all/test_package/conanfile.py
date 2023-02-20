from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.files import copy
from conan.tools.microsoft import is_msvc
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps


required_conan_version = ">=1.54.0"


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "Imakefile", "Imake.tmpl"

    def build_requirements(self):
        if not self.conf.get("tools.gnu:make_program", check_type=str):
            self.tool_requires("make/4.2.1")

    def generate(self):
        deps = AutotoolsDeps(self)
        deps.generate()

        tc = AutotoolsToolchain(self)

        env = tc.environment()
        if is_msvc(self):
            env.define("CC", "cl -nologo")
        tc.generate(env)

    def build(self):
        copy(self, "Imake*", self.source_folder, self.build_folder)
        if can_run(self):
            self.run("imake", env="conanrun")
        autotools = Autotools(self)
        autotools.make()

    def test(self):
        if can_run(self):
            autotools = Autotools(self)
            autotools.make()
