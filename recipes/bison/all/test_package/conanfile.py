from conans import ConanFile, CMake, tools
import os
from six import StringIO


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build_requirements(self):
        if not tools.cross_building(self.settings):
            if tools.os_info.is_windows:
                if "CONAN_BASH_PATH" not in os.environ:
                    self.build_requires("msys2_installer/latest@bincrafters/stable")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
            
            # verify bison may run
            self.run("bison --version", run_environment=True)
            # verify yacc may run
            self.run("yacc --version", run_environment=True, win_bash=tools.os_info.is_windows)
            # verify bison may preprocess something
            mc_parser = os.path.join(self.source_folder, "mc_parser.yy")
            self.run("bison -d %s" % mc_parser, run_environment=True)
            # verify bison doesn't have hard-coded paths
            bison = tools.which("bison")
            if tools.which("strings") and tools.which("grep"):
                output = StringIO()
                self.run('strings %s | grep "\.bison" | true' % bison, output=output)
                output = output.getvalue().strip()
                if output:
                    raise Exception("bison has hard-coded paths to conan: %s" % output)
            # verify bison works without M4 environment variables
            with tools.environment_append({"M4": None}):
                self.run("bison -d %s" % mc_parser, run_environment=True)
