import platform

from conan import ConanFile
from conan.tools.build import cross_building
from conans.model.version import Version


class TestPackageConan(ConanFile):

    settings = "os", "arch"
    test_type = "explicit"

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)

    def test(self):
        if not cross_building(self):
            if self.settings.os in ["Linux", "FreeBSD"]:
                libc_version = Version(platform.libc_ver()[1])
                if libc_version < "2.29":
                    self.output.warning(f"System libc version {libc_version} < 2.29, skipping test_package")
                    return
            self.output.info("Node version:")
            self.run("node --version")
