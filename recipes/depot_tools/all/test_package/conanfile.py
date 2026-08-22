from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"

    def layout(self):
        basic_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if Version(self.dependencies.build[self.tested_reference_str].ref.version) != "cci.20241206":
            # INFO: cit was deprecated on 2023-07-28
            # See the commit d062c2eb80f09740268101be72db13167c898a5d
            self.run("cit --help")
        # INFO: The depot tools has its own python interpreter and it will download several dependencies at the first run
        # When running gclient or other tools, their shebang is prepared to use the python interpreter from depot tools
        assert os.path.exists(os.path.join(self.dependencies.build[self.tested_reference_str].cpp_info.bindir, "gclient"))
