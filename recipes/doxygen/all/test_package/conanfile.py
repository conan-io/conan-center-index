from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"

    def build(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            if not os.path.isdir(os.path.join(self.build_folder, "html")):
                raise ConanException("doxygen did not create html documentation directory")

            self.output.info("Version:")
            self.run("doxygen --version", run_environment=True)
