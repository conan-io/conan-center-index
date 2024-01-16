from conan import ConanFile
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def layout(self):
        basic_layout(self)

    def test(self):
        # FIXME: Can't actually run this since Ruby and required Ruby gems are not set up
        if self.settings.os == "Windows":
            self.run("where ign", scope="conanrun")
        else:
            self.run("which ign", scope="conanrun")
