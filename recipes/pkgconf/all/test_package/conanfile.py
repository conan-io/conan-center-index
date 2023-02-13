from io import StringIO
import os
from pathlib import Path
import re

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout


# It will become the standard on Conan 2.x
class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires(self.tested_reference_str) # for the library

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str) # for the executable
        self.tool_requires("automake/1.16.5")
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            self.tool_requires("msys2/cci.latest")

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        # Autotools project to test integration pkgconfig works
        # during an Autotools configure run
        at = AutotoolsToolchain(self)
        at.generate()

        # Expose `PKG_CONFIG_PATH` to be able to find libexample1.pc
        env = Environment()
        self.output.warning(f"Source folder: {self.source_folder}")
        env.prepend_path("PKG_CONFIG_PATH", self.source_folder)
        env.vars(self, scope="build").save_script("pkgconf-config-path")

        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

        # CMake project to test that we can link against the library,
        # when the library is built
        if self.dependencies[self.tested_reference_str].options.enable_lib:
            ct = CMakeToolchain(self)
            ct.generate()
            deps = CMakeDeps(self)
            deps.generate()

    @property
    def _testing_library(self):
        # Workaround, in Conan >=2.0 we should be able to remove this in favour of:
        # self.dependencies[self.tested_reference_str].options.enable_lib
        has_toolchain = sorted(Path(self.build_folder).rglob('conan_toolchain.cmake'))
        return has_toolchain
        
    def build(self):
        # Test that configure doesn't fail, we are not building the 
        # autotools project
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        
        if self._testing_library:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        # Check that we can find pkgconf in build environment
        # and that it is the expected version
        output = StringIO()
        self.run("pkgconf --about", output, env="conanbuild")
        pkgconf_about = output.getvalue().splitlines()[0]
        self.output.info(f"pkgconf about: {pkgconf_about}")
        # TODO: When recipe is Conan 2+ only, this can be simplified
        # to: self.dependencies['pkgconf'].ref.version
        tokens = re.split('[@#]', self.tested_reference_str)
        pkgconf_expected_version = tokens[0].split("/", 1)[1]
        assert f"pkgconf {pkgconf_expected_version}" == pkgconf_about
        
        # Test that executable linked against library runs as expected
        if can_run(self) and self._testing_library:
            self.run(os.path.join(self.build_folder, "test_package"), env="conanrun")
