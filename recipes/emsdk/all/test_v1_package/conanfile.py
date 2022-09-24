from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"
    generators = "cmake"

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)

    def build(self):
        # It only makes sense to build a library, if the target os is Emscripten
        if self.settings.os == "Emscripten":
            with tools.environment_append({"EM_CACHE": os.path.join(self.build_folder, ".emcache")}):
                cmake = CMake(self)
                cmake.configure()
                cmake.build()

    def test(self):
        # Check the package provides working binaries
        if not tools.cross_building(self):
            self.run("emcc -v", run_environment=True)
            self.run("em++ -v", run_environment=True)

        # Run the project that was built using emsdk
        if self.settings.os == "Emscripten":
            test_file = os.path.join("bin", "test_package.js")
            self.run(f"node {test_file}", run_environment=True)
