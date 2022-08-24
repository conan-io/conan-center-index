from conan import ConanFile, tools$
import os


class DefaultNameConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"

    def build(self):
        pass

    def test(self):
        if tools.build.cross_building(self, self.settings):
            return
        tools.files.mkdir(self, "libs")
        tools.files.save(self, "Jamroot", "")
        with tools.environment_append({"BOOST_ROOT": self.build_folder}):
            self.run("boostdep --list-modules", run_environment=True)
