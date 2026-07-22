from io import StringIO

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import Environment


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        # Disable Conan's automatic run env so a profile's [runenv] PATH entry
        # can't outrank this package's bindir below.
        self.virtualrunenv = False
        env = Environment()
        env.prepend_path("PATH", self.dependencies[self.tested_reference_str].cpp_info.bindir)
        env.vars(self, scope="run").save_script("conanrunenv")

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
