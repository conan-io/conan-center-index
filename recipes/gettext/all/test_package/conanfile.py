from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import VirtualRunEnv
from conan.tools.layout import basic_layout



class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
         self.requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self, src_folder="src")
        
    def generate(self):
        runenv = VirtualRunEnv(self)
        runenv.generate()

    def test(self):
        if can_run(self):
            for exe in ["gettext", "ngettext", "msgcat", "msgmerge"]:
                self.run("{} --version".format(exe), env="conanrun")
