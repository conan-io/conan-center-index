import os.path

from conan import ConanFile, tools
from conans import CMake, RunEnvironment
from conans.errors import ConanException


class FlatccTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        if tools.cross_building(self):
            return

        env_build = RunEnvironment(self)
        with tools.environment_append(env_build.vars):
            cmake = CMake(self)
            if tools.os_info.is_macos and self.options["flatcc"].shared:
                # Because of MacOS System Integraty Protection it is currently not possible to run the flatcc
                # executable from cmake if it is linked shared. As a temporary work-around run flatcc here in
                # the build function.
                tools.files.mkdir(self, os.path.join(self.build_folder, "generated"))
                self.run("flatcc -a -o " + os.path.join(self.build_folder, "generated") + " " + os.path.join(self.source_folder, "monster.fbs"), run_environment=True)
                cmake.definitions["MACOS_SIP_WORKAROUND"] = True
            cmake.configure()
            cmake.build()

    def test(self):
        if tools.cross_building(self):
            bin_path = os.path.join(self.deps_cpp_info["flatcc"].rootpath, "bin", "flatcc")
            if not os.path.isfile(bin_path) or not os.access(bin_path, os.X_OK):
                raise ConanException("flatcc doesn't exist.")
        else:
            bin_path = os.path.join(self.build_folder, "bin", "monster")
            self.run(bin_path, cwd=self.source_folder, run_environment=True)
