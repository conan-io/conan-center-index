from conans import ConanFile, tools
import os


class DefaultNameConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"

    def build(self):
        pass

    def test(self):
        if tools.cross_building(self.settings):
            return
        tools.mkdir("libs")
        tools.save("Jamroot", "")
        with tools.environment_append({"BOOST_ROOT": self.build_folder}):
            self.run("boostdep --list-modules", run_environment=True)
