from io import StringIO

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def layout(self):
        basic_layout(self)

    def generate(self):
        # Expose `PKG_CONFIG_PATH` to be able to find libexample1.pc
        env = Environment()
        env.prepend_path("PKG_CONFIG_PATH", self.recipe_folder)
        env.vars(self, scope="run").save_script("pkgconf-config-path")
        # Check build environment postconditions
        buildenv = VirtualBuildEnv(self)
        env = buildenv.vars(scope='build')
        assert 'PKG_CONFIG' in env.keys()
        assert 'ACLOCAL_PATH' in env.keys()
        assert 'AUTOMAKE_CONAN_INCLUDES' in env.keys()
        buildenv.generate()

    def test(self):
        # Check that we can find pkgconf in build environment
        # and that it is the expected version
        if can_run(self):
            output = StringIO()
            self.run("pkgconf --about", output, env="conanrun")
            pkgconf_expected_version = self.dependencies[self.tested_reference_str].ref.version
            assert f"pkgconf {pkgconf_expected_version}" in output.getvalue()

            self.run("pkgconf libexample1 -cflags", env="conanrun")
