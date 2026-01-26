from io import StringIO

from conan import ConanFile
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            output = StringIO()
            self.run("wayland-scanner++", stderr=output, env="conanrun", ignore_errors=True)
            output_str = str(output.getvalue())
            self.output.info(output_str)
            assert(output_str.startswith("Usage:"))
