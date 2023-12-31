from io import StringIO

from conan import ConanFile
from conan.tools.build import cross_building
from conans.model.version import Version


class TestPackageConan(ConanFile):

    settings = "os", "arch"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def _get_libc_version(self):
        stdout = StringIO()
        self.run("ldd --version 2>&1", stdout, env="buildenv")
        stdout = stdout.getvalue()
        try:
            return Version(stdout.splitlines()[0].split()[-1])
        except IndexError:
            self.output.warning("Failed to parse libc version from 'ldd --version' output:\n" + stdout)
            return None

    def test(self):
        if not cross_building(self):
            if self.settings.os in ["Linux", "FreeBSD"]:
                libc_version = self._get_libc_version()
                if libc_version and libc_version < "2.29":
                    self.output.warning(f"System libc version {libc_version} < 2.29, skipping test_package")
                    return
            self.output.info("Node version:")
            self.run("node --version")
