from conan import ConanFile
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def generate(self):
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()

    def test(self):
        pkg_config = self.conf_info.get("tools.gnu:pkg_config", default="pkg-config")
        self.run(f"{pkg_config} --validate xkeyboard-config")
