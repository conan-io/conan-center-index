from conans import ConanFile, CMake, tools
import os


class MimallocTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    _test_file = "test_basic"
    _build_basic = False
    _build_redefine_malloc = False

    def configure(self):
        if self.options["mimalloc"].redefine_malloc:
            self._test_file = "test_redefine_malloc"
            self._build_redefine_malloc = True
        else:
            self._build_basic = True

    def build(self):
        self.output.warn(f"self._build_redefine_malloc: {self._build_redefine_malloc}")
        cmake = CMake(self)
        cmake.definitions["BUILD_BASIC"] = self._build_basic
        cmake.definitions["BUILD_REDEFINE_MALLOC"] = self._build_redefine_malloc
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            test_package = os.path.join("bin", self._test_file)
            self.run(test_package, run_environment=True)

            if not self._build_redefine_malloc:
                test_package_cpp = os.path.join("bin", self._test_file + "_cpp")
                self.run(test_package_cpp, run_environment=True)
