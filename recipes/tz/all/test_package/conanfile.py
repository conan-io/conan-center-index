from conan import ConanFile
from conan.tools.build import can_run
from conan.errors import ConanException
import io


class TzTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            stdout = io.StringIO()
            self.run("zdump --help", env="conanrun", stdout=stdout)
            assert "zdump: usage: zdump OPTIONS TIMEZONE ..." in stdout.getvalue()
