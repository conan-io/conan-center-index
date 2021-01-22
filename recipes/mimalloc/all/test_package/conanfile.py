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
            self._test_files = ["include_override", "mi_api"]
        elif self.settings.compiler == "Visual Studio" and not self.options["mimalloc"].shared:
            self._test_files = ["include_override", "mi_api"]

        # Unix-like:
        elif self.options["mimalloc"].override and self.options["mimalloc"].inject:
            self._test_files = ["no_changes"]
        else:
            self._test_files = ["no_changes", "include_override", "mi_api"]

        cmake = CMake(self)
        cmake.definitions["BUILD_NO_CHANGES"] = "no_changes" in self._test_files
        cmake.definitions["BUILD_INCLUDE_OVERRIDE"] = "include_override" in self._test_files
        cmake.definitions["BUILD_MI_API"] = "mi_api" in self._test_files
        cmake.configure()
        cmake.build()

    @property
    def _lib_name(self):
        name = "mimalloc" if self.settings.os == "Windows" else "libmimalloc"
        if self.settings.os == "Windows" and not self.options.shared:
            name += "-static"
        if self.options.secure:
            name += "-secure"
        if self.settings.build_type not in ("Release", "RelWithDebInfo", "MinSizeRel"):
            name += "-{}".format(str(self.settings.build_type).lower())
        return name

    @property
    def _environment(self):
        environment = {"MIMALLOC_VERBOSE": "1"}

        if self.settings.compiler == "Visual Studio" or \
           not self.options["mimalloc"].override or \
           not self.options["mimalloc"].inject:
            return environment

        if self.settings.os == "Linux":
            environment["LD_PRELOAD"] = self._lib_name + ".so"
        elif self.settings.os == "Macos":
            environment["DYLD_FORCE_FLAT_NAMESPACE"] = "1"
            environment["DYLD_INSERT_LIBRARIES"] = self._lib_name +".dylib"

        return environment

    def test(self):
        if tools.cross_building(self.settings):
            return

        with tools.environment_append(self._environment):
            for file in self._test_files:
                test_package = os.path.join("bin", file)
                self.output.info(f"test: {test_package}")
                self.run(test_package, run_environment=True)

                test_package_cpp = os.path.join("bin", file + "_cpp")
                self.output.info(f"test: {test_package_cpp}")
                self.run(test_package_cpp, run_environment=True)
