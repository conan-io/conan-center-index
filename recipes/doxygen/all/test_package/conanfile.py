from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    generators = "cmake"

    def build(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            if not os.path.isdir(os.path.join(self.build_folder, "html")):
                raise ConanException("doxygen did not create html documentation directory")

            self.output.info("Version:")
            self.run("doxygen --version", run_environment=True)
