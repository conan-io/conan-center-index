from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.files import copy
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, Autotools
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.50.0"


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac", "Makefile.am", "test_package_1.c", "test_package.cpp"
    test_type = "explicit"

    @property
    def _settings_build(self):
        # TODO: Remove for Conan v2
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        basic_layout(self, src_folder=".")

    def generate(self):
        tc = AutotoolsToolchain(self)
        env = tc.environment()
        if is_msvc(self):
            env.define("CC", "cl -nologo")
            env.define("CXX", "cl -nologo")
            env.define("LD", "link")
        tc.generate(env)
        tc = AutotoolsDeps(self)
        tc.generate()

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        self.tool_requires("autoconf/2.71") # Needed for autoreconf
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")  # The conf `tools.microsoft.bash:path` and `tools.microsoft.bash:subsystem` aren't injected for test_package

    def build(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            return  # autoconf needs a bash if there isn't a bash no need to build

        for src in self.exports_sources:
            copy(self, src, self.source_path, self.build_folder)

        autotools = Autotools(self)
        self.run("autoreconf -fiv", cwd=self.build_path)  # Workaround for since the method `autoreconf()` will always run from source
        autotools.configure(build_script_folder=self.build_path)
        autotools.make()

    def test(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            return  # autoconf needs a bash if there isn't a bash no need to build

        if can_run(self):
            ext = ".exe" if self.settings.os == "Windows" else ""
            test_cmd = unix_path(self, self.build_path.joinpath(f"test_package{ext}"))

            self.run(test_cmd, scope="run", env="conanbuild")
