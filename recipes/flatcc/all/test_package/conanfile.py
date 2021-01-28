import os.path

from conans import ConanFile, CMake, tools, RunEnvironment


class FlatccTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        env_build = RunEnvironment(self)
        with tools.environment_append(env_build.vars):
            cmake = CMake(self)
            if tools.os_info.is_macos and self.options["flatcc"].shared:
                # Because of MacOS System Integraty Protection it is currently not possible to run the flatcc
                # executable from cmake if it is linked shared. As a temporary work-around run flatcc here in
                # the build function.
                tools.mkdir(os.path.join(self.build_folder, "generated"))
                self.run("flatcc -a -o " + os.path.join(self.build_folder, "generated") + " " + os.path.join(self.source_folder, "monster.fbs"), run_environment=True)
                cmake.definitions["MACOS_SIP_WORKAROUND"] = True
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join(self.build_folder, "bin", "monster")
            self.run(bin_path, cwd=self.source_folder, run_environment=True)
