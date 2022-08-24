from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os
import shutil


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.build_requires(str(self.requires["ftjam"]))

    def build(self):
        for f in ("header.h", "main.c", "source.c", "Jamfile"):
            shutil.copy(os.path.join(self.source_folder, f),
                        os.path.join(self.build_folder, f))
        if not tools.build.cross_building(self, self):
            assert os.path.isfile(tools.get_env("JAM"))

            vars = AutoToolsBuildEnvironment(self).vars
            vars["CCFLAGS"] = vars["CFLAGS"]
            vars["C++FLAGS"] = vars["CXXFLAGS"]
            vars["LINKFLAGS"] = vars["LDFLAGS"]
            vars["LINKLIBS"] = vars["LIBS"]
            with tools.environment_append(vars):
                self.run("{} -d7".format(tools.get_env("JAM")), run_environment=True)

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join(".", "test_package")
            self.run(bin_path, run_environment=True)
