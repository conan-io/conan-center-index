from io import StringIO

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout
from conan.tools.scm import Version


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def _get_libc_version(self):
        stdout = StringIO()
        self.run("ldd --version", stdout)
        return Version(stdout.getvalue().splitlines()[0].split()[-1])

    def test(self):
        if can_run(self):
            if self.settings.os in ["Linux", "FreeBSD"]:
                libc_version = self._get_libc_version()
                if libc_version < "2.29":
                    self.output.warn(f"System libc version {libc_version} < 2.29, skipping test_package")
                    return
            self.run("node --version")
