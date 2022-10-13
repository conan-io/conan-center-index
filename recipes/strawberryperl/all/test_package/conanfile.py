import os
from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import VirtualBuildEnv
from conan.tools.scm import Version

from conans import __version__ as conan_version


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"
    # apply_env = False

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        # if Version(conan_version) >= "2.0.0-beta":
        #     perl_path = self.dependencies[self.tested_reference_str].conf_info.get("user.cci:perl")
        #     self.run(f"{perl_path} --version")
        if can_run(self):
            # build_env = VirtualBuildEnv(self).vars() # AttributeError: 'NoneType' object has no attribute 'dependencies'
            # with build_env.apply():
            # self.run("set PATH", env="conanbuild")
            self.run("perl --version")
            perl_script = os.path.join(self.source_folder, "list_files.pl")
            self.run(f"perl {perl_script}", env="conanbuild")
