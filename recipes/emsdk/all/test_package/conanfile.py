from conan import ConanFile
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        # Check the package provides working binaries
        if can_run(self):
            self.run("emcc -v", env="conanrun")
            self.run("em++ -v", env="conanrun")
            self.run("node -v", env="conanrun")
