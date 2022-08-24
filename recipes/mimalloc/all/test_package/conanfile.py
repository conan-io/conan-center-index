from conan import ConanFile
from conans import CMake, RunEnvironment, tools
import os


class MimallocTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        # No override:
        if not self.options["mimalloc"].override:
            self._test_files = ["mi_api"]

        # Visual Studio overriding:
        elif self.settings.compiler == "Visual Studio" and self.options["mimalloc"].shared:
            self._test_files = ["include_override", "mi_api"]
        elif self.settings.compiler == "Visual Studio" and not self.options["mimalloc"].shared:
            self._test_files = ["include_override", "mi_api"]

        # Non Macos injected override:
        elif self.settings.os != "Macos" and \
             self.options["mimalloc"].override and \
             self.options["mimalloc"].shared and \
             self.options["mimalloc"].inject:
            self._test_files = ["no_changes"]

        # Could not simulate Macos preload, so just ignore it:
        elif self.settings.os == "Macos" and \
             self.options["mimalloc"].override and \
             self.options["mimalloc"].shared and \
             self.options["mimalloc"].inject:
            self._test_files = []

        # Unix-like non injected override:
        else:
            self._test_files = ["include_override", "mi_api"]

        cmake = CMake(self)
        cmake.definitions["BUILD_NO_CHANGES"] = "no_changes" in self._test_files
        cmake.definitions["BUILD_INCLUDE_OVERRIDE"] = "include_override" in self._test_files
        cmake.definitions["BUILD_MI_API"] = "mi_api" in self._test_files
        cmake.configure()
        cmake.build()

    @property
    def _lib_name(self):
        name = "mimalloc" if self.settings.os == "Windows" else "libmimalloc"
        if self.settings.os == "Windows" and not self.options["mimalloc"].shared:
            name += "-static"
        if self.options["mimalloc"].secure:
            name += "-secure"
        if self.settings.build_type not in ("Release", "RelWithDebInfo", "MinSizeRel"):
            name += "-{}".format(str(self.settings.build_type).lower())
        return name

    @property
    def _environment(self):
        environment = {"MIMALLOC_VERBOSE": "1"}

        if self.settings.compiler == "Visual Studio" or \
           not self.options["mimalloc"].shared or \
           not self.options["mimalloc"].override or \
           not self.options["mimalloc"].inject:
            return environment

        if self.settings.os == "Linux":
            environment["LD_PRELOAD"] = self._lib_name + ".so"
        elif self.settings.os == "Macos":
            env_build = RunEnvironment(self)
            insert_library = os.path.join(env_build.vars["DYLD_LIBRARY_PATH"][0], self._lib_name +".dylib")

            environment["DYLD_FORCE_FLAT_NAMESPACE"] = "1"
            environment["DYLD_INSERT_LIBRARIES"] = insert_library

        return environment

    def test(self):
        if tools.build.cross_building(self, self):
            return

        self.output.info("Environment append: {}".format(self._environment))

        with tools.environment_append(self._environment):
            for file in self._test_files:
                test_package = os.path.join("bin", file)
                self.output.info("test: {}".format(test_package))
                self.run(test_package, run_environment=True)

                test_package_cpp = os.path.join("bin", file + "_cpp")
                self.output.info("test: {}".format(test_package_cpp))
                self.run(test_package_cpp, run_environment=True)
