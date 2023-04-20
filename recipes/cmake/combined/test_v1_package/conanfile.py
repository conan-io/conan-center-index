from six import StringIO
from conan import ConanFile
import re


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        output = StringIO()
        self.run("cmake --version", output=output, run_environment=False)
        output_str = str(output.getvalue())
        self.output.info(f"Installed version: {output_str}")
        tokens = re.split('[@#]', self.tested_reference_str)
        require_version = tokens[0].split("/", 1)[1]
        self.output.info(f"Expected version: {require_version}")
        assert_cmake_version = f"cmake version {require_version}"
        assert assert_cmake_version in output_str
