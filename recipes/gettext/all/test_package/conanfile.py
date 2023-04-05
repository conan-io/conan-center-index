from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import Environment, VirtualRunEnv, VirtualBuildEnv
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc



class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "configure.ac",
    test_type = "explicit"
    win_bash = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
         self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        self.tool_requires("automake/1.16.5")
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            self.tool_requires("msys2/cci.latest")

    def layout(self):
        basic_layout(self, src_folder="src")
        
    def generate(self):
        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

        at = AutotoolsToolchain(self)
        at.generate()

        if is_msvc(self):
            env = Environment()
            env.define("CC", "cl -nologo")
            env.define("LD", "link -nologo")
            env.vars(self).save_script("conanbuild_libsmacker_msvc")

        runenv = VirtualRunEnv(self)
        runenv.generate()

    def build(self):

        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()


    def test(self):
        if can_run(self):
            for exe in ["gettext", "ngettext", "msgcat", "msgmerge"]:
                self.run("{} --version".format(exe), env="conanrun")
