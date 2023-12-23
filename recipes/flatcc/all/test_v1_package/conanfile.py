import os.path

from conans import ConanFile, CMake, tools, RunEnvironment
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
                # Because of MacOS System Integrity Protection it is currently not possible to run the flatcc
                # executable from cmake if it is linked shared. As a temporary work-around run flatcc here in
                # the build function.
                gen_dir = os.path.join(self.build_folder, "generated")
                tools.mkdir(gen_dir)
                fbs_file = os.path.join(self.source_folder, "monster.fbs")
                self.run(f"flatcc -a -o {gen_dir} {fbs_file}", run_environment=True)
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
