import os
import shutil

from conan import ConanFile
from conan.tools.build import can_run, cross_building
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def build(self):
        for f in ("header.h", "main.c", "source.c", "Jamfile"):
            shutil.copy(os.path.join(self.source_folder, f), os.path.join(self.build_folder, f))
        if not cross_building(self):
            # assert os.path.isfile(os.environ.get("JAM"))
            # vars = AutoToolsBuildEnvironment(self).vars
            # vars["CCFLAGS"] = vars["CFLAGS"]
            # vars["C++FLAGS"] = vars["CXXFLAGS"]
            # vars["LINKFLAGS"] = vars["LDFLAGS"]
            # vars["LINKLIBS"] = vars["LIBS"]
            # with environment_append(self, vars):
            self.run("jam -d7")

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
