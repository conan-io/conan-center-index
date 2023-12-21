from conans import ConanFile, CMake, RunEnvironment, tools
from conans.errors import ConanException
import os
import functools


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def _mimalloc_option(self, name, default=None):
        try:
            return getattr(self.options["mimalloc"], name, default)
        except (AttributeError, ConanException):
            return default

    @functools.lru_cache(1)
    def _test_files(self):
        # No override:
        if not self.options["mimalloc"].override:
            return ["mi_api"]
        # Injected override:
        elif self._mimalloc_option("inject"):
            if self.settings.os == "Macos":
                # Could not simulate Macos preload, so just ignore it
                return []
            return ["no_changes"]
        # Non injected override:
        return ["include_override", "mi_api"]

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_NO_CHANGES"] = "no_changes" in self._test_files()
        cmake.definitions["BUILD_INCLUDE_OVERRIDE"] = "include_override" in self._test_files()
        cmake.definitions["BUILD_MI_API"] = "mi_api" in self._test_files()
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
            name += f"-{str(self.settings.build_type).lower()}"
        return name

    @property
    def _environment(self):
        environment = {"MIMALLOC_VERBOSE": "1"}

        if self._mimalloc_option("inject"):
            if self.settings.os == "Linux":
                environment["LD_PRELOAD"] = f"{self._lib_name}.so"
            elif self.settings.os == "Macos":
                env_build = RunEnvironment(self)
                insert_library = os.path.join(env_build.vars["DYLD_LIBRARY_PATH"][0], f"{self._lib_name}.dylib")

                environment["DYLD_FORCE_FLAT_NAMESPACE"] = "1"
                environment["DYLD_INSERT_LIBRARIES"] = insert_library

        return environment

    def test(self):
        if tools.cross_building(self):
            return
        with tools.environment_append(self._environment):
            self.run(f"ctest --output-on-failure -C {self.settings.build_type} -j {tools.cpu_count()}", run_environment=True)
