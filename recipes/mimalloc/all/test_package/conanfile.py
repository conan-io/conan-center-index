from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, Environment

import os
import functools

class MimallocTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    @functools.lru_cache(1)
    def _test_files(self):
        test_files = []

        # No override:
        if not self.options["mimalloc"].override:
            test_files = ["mi_api"]

        # Visual Studio overriding:
        elif self.settings.compiler == "Visual Studio" and self.options["mimalloc"].shared:
            test_files = ["include_override", "mi_api"]
        elif self.settings.compiler == "Visual Studio" and not self.options["mimalloc"].shared:
            test_files = ["include_override", "mi_api"]

        # Non Macos injected override:
        elif self.settings.os != "Macos" and \
             self.options["mimalloc"].override and \
             self.options["mimalloc"].shared and \
             self.options["mimalloc"].inject:
            test_files = ["no_changes"]

        # Could not simulate Macos preload, so just ignore it:
        elif self.settings.os == "Macos" and \
             self.options["mimalloc"].override and \
             self.options["mimalloc"].shared and \
             self.options["mimalloc"].inject:
            test_files = []

        # Unix-like non injected override:
        else:
            test_files = ["include_override", "mi_api"]

        return test_files

    def generate(self):
        test_files = self._test_files()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_NO_CHANGES"] = "no_changes" in test_files
        tc.variables["BUILD_INCLUDE_OVERRIDE"] = "include_override" in test_files
        tc.variables["BUILD_MI_API"] = "mi_api" in test_files
        tc.generate()

        env = Environment()
        env.define("MIMALLOC_VERBOSE", "1")

        if self.settings.os == "Linux":
            env.define("LD_PRELOAD", f"{self._lib_name}.so")
        elif self.settings.os == "Macos":
            env.define("DYLD_FORCE_FLAT_NAMESPACE", "1")
            insert_library = os.path.join(self.deps_cpp_info["mimalloc"].libdirs[0], self._lib_name +".dylib")
            env.define("DYLD_INSERT_LIBRARIES", insert_library)

        envvars = env.vars(self, scope="run")
        envvars.save_script("mimalloc_env_file")

        deps = CMakeDeps(self)
        deps.generate()

        vbe = VirtualBuildEnv(self)
        vbe.generate(scope="build")

    def build(self):
        cmake = CMake(self)
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

    def test(self):
        if not can_run(self):
            return

        test_files = self._test_files()
        for file in test_files:
            test_package = os.path.join(self.cpp.build.bindirs[0], file)
            self.output.info("test: {}".format(test_package))
            self.run(test_package, run_environment=True)

            test_package_cpp = os.path.join(self.cpp.build.bindirs[0], f"{file}_cpp")
            self.output.info("test: {}".format(test_package_cpp))
            self.run(test_package_cpp, run_environment=True)
