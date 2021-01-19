from conans import ConanFile, CMake, tools
import os


class MimallocTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        # No override:
        if not self.options["mimalloc"].override:
            self._test_files = ["mi_api"]

        # Visual Studio:
        elif self.settings.compiler == "Visual Studio" and self.options["mimalloc"].shared:
            self._test_files = ["no_changes", "include_override", "mi_api"]
        elif self.settings.compiler == "Visual Studio" and not self.options["mimalloc"].shared:
            self._test_files = ["include_override", "mi_api"]

        # Unix-like:
        elif self.options["mimalloc"].inject:
            self._test_files = ["no_changes"]
        else:
            self._test_files = ["no_changes", "include_override", "mi_api"]

        cmake = CMake(self)
        cmake.definitions["BUILD_NO_CHANGES"] = "no_changes" in self._test_files
        cmake.definitions["BUILD_INCLUDE_OVERRIDE"] = "include_override" in self._test_files
        cmake.definitions["BUILD_MI_API"] = "mi_api" in self._test_files
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            return

        with tools.environment_append({"MIMALLOC_VERBOSE": "1"}):
            for file in self._test_files:
                test_package = os.path.join("bin", file)
                self.run(test_package, run_environment=True)

                test_package_cpp = os.path.join("bin", file + "_cpp")
                self.run(test_package_cpp, run_environment=True)
