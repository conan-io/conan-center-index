from io import StringIO

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import VirtualBuildEnv
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def layout(self):
        basic_layout(self)

    def generate(self):
        # Check build environment postconditions
        buildenv = VirtualBuildEnv(self)
        env = buildenv.vars(scope='build')
        assert 'PKG_CONFIG' in env.keys()
        assert 'ACLOCAL_PATH' in env.keys()
        buildenv.generate()

    def test(self):
        # Check that we can find pkgconf
        # and that it is the expected version
        if can_run(self):
            output = StringIO()
            self.run("pkgconf --about", output, env="conanrun")
            pkgconf_expected_version = self.dependencies[self.tested_reference_str].ref.version
            assert f"pkgconf {pkgconf_expected_version}" in output.getvalue()
