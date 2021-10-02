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
        self.build_requires("cmake/3.18.2")
        if self._settings_build.os == "Windows":
            self.build_requires("make/4.3")

    def build(self):
        clang = os.path.join(self.deps_cpp_info["emsdk"].rootpath, "bin", "upstream", "bin", "clang")
        if self.settings.os == "Macos":
            self.run("file %s" % clang)
            self.run("otool -falh %s" % clang)
        self.run("emcc -v", run_environment=True)
        self.run("em++ -v", run_environment=True)
        cmake = CMake(self, generator="Unix Makefiles")
        cmake.definitions["USE_CONANBUILDINFO"] = self.settings.os == "Emscripten"
        cmake.configure()
        cmake.build()

    def test(self):
        test_file = os.path.join("bin", "test_package.js")
        assert os.path.isfile(test_file)
        if tools.which("node"):
            self.run("node %s" % test_file, run_environment=True)
