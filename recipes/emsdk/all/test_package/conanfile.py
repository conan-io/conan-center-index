from conans import ConanFile, CMake, tools, RunEnvironment
import os

required_conan_version = ">=1.36.0"


class TestPackageConan(ConanFile):
    settings = "os", "build_type", "arch", "compiler"
    generators = "cmake"

    def build(self):
        if self.settings.os == "Emscripten":
            cmake = CMake(self, generator='MinGW Makefiles' if os.name ==
                          'nt' else 'Unix Makefiles', parallel=False)
            cmake.definitions["CONAN_DISABLE_CHECK_COMPILER"] = True
            cmake.configure()
            cmake.build()

    def test(self):
        if self.settings.os == "Emscripten":
            test_file = os.path.join(
                self.build_folder, "bin", "test_package.js")
            self.run('node %s' % test_file, run_environment=True)
