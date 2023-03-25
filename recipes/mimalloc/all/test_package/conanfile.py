from conan import ConanFile
from conan.tools.build import build_jobs, can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import Environment
from conan.tools.files import chdir
import os
import functools


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    @functools.lru_cache(1)
    def _test_files(self):
        # No override:
        if not self.dependencies["mimalloc"].options.override:
            return ["mi_api"]
        # Injected override
        elif self.dependencies["mimalloc"].options.get_safe("inject"):
            if self.settings.os == "Macos":
                # Could not simulate Macos preload, so just ignore it
                return []
            return ["no_changes"]
        # Non injected override
        return ["include_override", "mi_api"]

    @property
    def _lib_name(self):
        name = "mimalloc" if self.settings.os == "Windows" else "libmimalloc"
        if self.settings.os == "Windows" and not self.dependencies["mimalloc"].options.shared:
            name += "-static"
        if self.dependencies["mimalloc"].options.secure:
            name += "-secure"
        if self.settings.build_type not in ("Release", "RelWithDebInfo", "MinSizeRel"):
            name += f"-{str(self.settings.build_type).lower()}"
        return name

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_NO_CHANGES"] = "no_changes" in self._test_files()
        tc.variables["BUILD_INCLUDE_OVERRIDE"] = "include_override" in self._test_files()
        tc.variables["BUILD_MI_API"] = "mi_api" in self._test_files()
        tc.generate()

        env = Environment()
        env.define("MIMALLOC_VERBOSE", "1")
        if self.dependencies["mimalloc"].options.get_safe("inject"):
            if self.settings.os == "Linux":
                env.define("LD_PRELOAD", f"{self._lib_name}.so")
            elif self.settings.os == "Macos":
                env.define("DYLD_FORCE_FLAT_NAMESPACE", "1")
                insert_library = os.path.join(self.dependencies["mimalloc"].cpp_info.libdirs[0], f"{self._lib_name}.dylib")
                env.define("DYLD_INSERT_LIBRARIES", insert_library)
        env.vars(self, scope="run").save_script("mimalloc_env_file")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            with chdir(self, self.build_folder):
                self.run(f"ctest --output-on-failure -C {self.settings.build_type} -j {build_jobs(self)}", env="conanrun")
