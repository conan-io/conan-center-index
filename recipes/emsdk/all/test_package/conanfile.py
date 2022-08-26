from conan import ConanFile
from conan.tools.env import Environment
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows":
            self.tool_requires("make/4.3")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        if self.settings.os == "Emscripten":
            env = Environment()
            env.define_path("EM_CACHE", os.path.join(self.build_folder, ".emcache"))
            envvars = env.vars(self, scope="build")
            envvars.save_script("em_cache")

    def build(self):
        # It only makes sense to build a library, if the target os is Emscripten
        if self.settings.os == "Emscripten":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        # Check the package provides working binaries
        self.run("emcc -v", env="conanbuild")
        self.run("em++ -v", env="conanbuild")

        # Run the project that was built using emsdk
        if self.settings.os == "Emscripten":
            test_file = os.path.join(self.cpp.build.bindirs[0], "test_package.js")
            self.run(f"node {test_file}", env="conanrun")
