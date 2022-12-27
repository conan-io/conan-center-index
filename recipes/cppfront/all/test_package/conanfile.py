from conan import ConanFile
from conan.tools.files import copy
from conan.tools.build import can_run
from conan.tools.layout import basic_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def layout(self):
        basic_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def build(self):
        if can_run(self):
            copy(self, "pure2-hello.cpp2", src=self.recipe_folder, dst=self.build_folder)
            self.run("cppfront {}".format(os.path.join(self.build_folder, "pure2-hello.cpp2")), env="conanbuild")

    def test(self):
        if can_run(self):
            self.run("cppfront -h", env="conanbuild")
            assert os.path.isfile(os.path.join(self.build_folder, "pure2-hello.cpp"))
