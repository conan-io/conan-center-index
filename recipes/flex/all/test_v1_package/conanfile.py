import os
import re
from io import StringIO

from conans import ConanFile, tools, CMake


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def _assert_expected_version(self):

        def tested_reference_version():
            tokens = re.split('[@#]', self.tested_reference_str)
            return tokens[0].split("/", 1)[1]

        output = StringIO()
        self.run(f"flex --version", output, run_environment=False)
        output_str = str(output.getvalue())
        self.output.info("Installed version: {}".format(output_str))
        expected_version = tested_reference_version()
        self.output.info("Expected version: {}".format(expected_version))
        assert_flex_version = "flex {}".format(expected_version)
        assert(assert_flex_version in output_str)

    def build(self):
        # Let's check flex version installed
        self._assert_expected_version()
        # FIXME: CMake legacy is not working as expected when cross-compiling
        if not tools.cross_building(self, skip_x64_x86=True):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            bin_path = os.path.join("bin", "test_package")
            txt_file = os.path.join(self.source_folder, "basic_nr.txt")
            self.run(f"{bin_path} {txt_file}", run_environment=True)
