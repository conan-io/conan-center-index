from conan import ConanFile
from conan.tools.files import save
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        save(self, "file.txt", "some text")
        assert not os.path.isdir("destionation")
        self.run("nsinstall -D destination")
        assert os.path.isdir("destination")
        assert not os.path.isfile(os.path.join("destination", "file.txt"))
        self.run("nsinstall -t -m 644 file.txt destination")
        assert os.path.isfile(os.path.join("destination", "file.txt"))
