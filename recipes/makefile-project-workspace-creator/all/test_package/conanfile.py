from conan import ConanFile, conan_version
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        basic_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if conan_version.major < 2 and self.settings.os == "Windows":
            self.tool_requires("strawberryperl/5.32.1.1")

    def test(self):
        self.run("perl -S mpc.pl --version")
