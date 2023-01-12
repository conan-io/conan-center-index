import re
from six import StringIO

from conan import ConanFile


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):

        def tested_reference_version():
            tokens = re.split('[@#]', self.tested_reference_str)
            return tokens[0].split("/", 1)[1]

        output = StringIO()
        self.run(f"flex --version", output=output, run_environment=False)
        output_str = str(output.getvalue()) 
        self.output.info("Installed version: {}".format(output_str))
        expected_version = tested_reference_version()
        self.output.info("Expected version: {}".format(expected_version))
        assert_flex_version = "flex {}".format(expected_version)
        assert(assert_flex_version in output_str)
