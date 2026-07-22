from io import StringIO

from conan import ConanFile
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if not can_run(self):
            return

        python = "python" if self.settings.os == "Windows" else "python3"

        output = StringIO()
        self.run(f"{python} --version", output, env="conanrun")
        version_output = output.getvalue().strip()
        self.output.info(f"Installed version: {version_output}")

        expected_version = self.dependencies[self.tested_reference_str].ref.version
        expected_output = f"Python {expected_version}"
        assert expected_output in version_output, \
            f"Expected '{expected_output}' in output, got '{version_output}'"
