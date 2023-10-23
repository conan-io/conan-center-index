from io import StringIO

from conan import ConanFile
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            output = StringIO()
            self.run("djinni --help", output)
            output.seek(0)
            found_usage = False
            for line in output:
                if "Usage: djinni [options]" in line:
                    found_usage = True
                    break
            assert found_usage
