from conan import ConanFile
from conan.tools.build import can_run
import os


class CcclTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VCVars", "VirtualBuildEnv"
    test_type = "explicit"
    win_bash = True

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self.settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            self.tool_requires("msys2/cci.latest")

    def build(self):
        if self.settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            return  # cccl needs a bash if there isn't a bash we can't build
        cxx = "cccl "
        src = os.path.join(self.source_folder, "example.cpp").replace("\\", "/")
        self.run(f"{cxx} {src} -o example", cwd=self.build_folder)

    def test(self):
        if self.settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            return  # cccl needs a bash if there isn't a bash we can't build
        if can_run(self):
            self.run("./example") #test self.run still runs in bash, so it needs "./"; seems weird but okay...
