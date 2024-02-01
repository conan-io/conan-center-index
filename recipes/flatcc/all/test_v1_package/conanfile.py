import os.path

from conans import ConanFile, CMake, tools, RunEnvironment
from conans.errors import ConanException


class FlatccTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _skip_shared_macos(self):
        # Because of MacOS System Integraty Protection it is currently not possible to run the flatcc
        # executable from cmake if it is linked shared. As a temporary work-around run flatcc here in
        # the build function.
        return self.options["flatcc"].shared and tools.os_info.is_macos

    def build(self):
        if tools.cross_building(self):
            return

        if self._skip_shared_macos:
            return

        env_build = RunEnvironment(self)
        with tools.environment_append(env_build.vars):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if self._skip_shared_macos:
            return
        if tools.cross_building(self):
            bin_path = os.path.join(self.deps_cpp_info["flatcc"].rootpath, "bin", "flatcc")
            if not os.path.isfile(bin_path) or not os.access(bin_path, os.X_OK):
                raise ConanException("flatcc doesn't exist.")
        else:
            bin_path = os.path.join(self.build_folder, "bin", "monster")
            self.run(bin_path, cwd=self.source_folder, run_environment=True)
