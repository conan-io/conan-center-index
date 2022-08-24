from conan import ConanFile, tools
from conans import CMake
from conan.tools.scm import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    
    # TODO remove when https://github.com/conan-io/conan/issues/7680 is solved (or VS2019 is updated to at least 16.7)
    def _skip_check(self):
        return self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) <= "16"

    def build(self):
        if self._skip_check():
            return
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if self._skip_check():
            return
        if not tools.build.cross_building(self, self.settings):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
