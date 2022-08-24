from conan import ConanFile
from conans import CMake, RunEnvironment, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self._minimum_cpp_standard)

    @property
    def _minimum_cpp_standard(self):
        return 11

    def build(self):
        env_build = RunEnvironment(self)
        with tools.environment_append(env_build.vars):
            cmake = CMake(self)
            cmake.configure(
                defs={
                    "CMAKE_CXX_STANDARD": self._cmake_cxx_standard,
                }
            )
            cmake.build()

    @property
    def _cmake_cxx_standard(self):
        compileropt = self.settings.compiler.get_safe("cppstd")
        if compileropt:
            return str(compileropt)
        else:
            return "11"

    def test(self):
        if not tools.build.cross_building(self, self):
            self._check_binaries_are_found()
            self._check_root_dictionaries()

    def _check_binaries_are_found(self):
        self.run("root -q", run_environment=True)

    def _check_root_dictionaries(self):
        bin_path = os.path.join("bin", "testrootdictionaries")
        self.run(bin_path, run_environment=True)
