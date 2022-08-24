from from conan import ConanFile, tools
from conans import CMake


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    @property
    def _can_build(self):
        # FIXME: Python does not distribute debug libraries (use cci CPython recipe)
        return not (self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug")

    def build(self):
        if not tools.build.cross_building(self, self, skip_x64_x86=True):
            self.run("swig -swiglib", run_environment=True)
            if self._can_build:
                cmake = CMake(self)
                cmake.verbose = True
                cmake.configure()
                cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            if self._can_build:
                cmake = CMake(self)
                cmake.test(output_on_failure=True)
            self.run("swig -version", run_environment=True)
