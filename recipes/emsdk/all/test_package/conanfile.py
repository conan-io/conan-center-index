from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.36.0"


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "build_requires"
    generators = "cmake"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.build_requires("make/4.3")

    def build(self):
        cmake = CMake(self, generator="Unix Makefiles")
        cmake.definitions["USE_CONANBUILDINFO"] = self.settings.os == "Emscripten"
        cmake.configure()
        cmake.build()

    def test(self):
        test_file = os.path.join("bin", "test_package.js")
        assert os.path.isfile(test_file)
        if tools.which("node"):
            self.run("node %s" % test_file, run_environment=True)
