import os

from conan import ConanFile
from conan.tools.files import load, save
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def generate(self):
        build_vars = self.dependencies.build[self.tested_reference_str].buildenv_info.vars(self)
        save(self, os.path.join(self.build_folder, "QtMsBuild"), build_vars["QtMsBuild"])

    def test(self):
        res_folder = load(self, os.path.join(self.build_folder, "QtMsBuild"))
        qt_props_path = os.path.join(res_folder, "qt.props")
        assert os.path.isfile(qt_props_path)
