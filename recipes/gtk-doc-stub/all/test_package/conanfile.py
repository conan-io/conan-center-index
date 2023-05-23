from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.files import copy
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac"
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        basic_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        self.tool_requires("automake/1.16.5")

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--enable-option-checking=fatal")
        tc.configure_args.append("--enable-gtk-doc=no")
        tc.generate()

    def build(self):
        copy(self, "configure.ac", self.export_sources_folder, self.build_folder)
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()

    def test(self):
        if can_run(self):
            self.run(f"gtkdocize --copy", env="conanrun")
