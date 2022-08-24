from conan import ConanFile, tools
from conans import CMake
import contextlib
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.build_requires(str(self.requires["grpc"]))

    @contextlib.contextmanager
    def _buildenv(self):
        # TODO: conan v2: replace by VirtualBuildEnv and always add grpc to build requirements
        if tools.build.cross_building(self, self):
            yield
        else:
            with tools.run_environment(self):
                yield

    def build(self):
        # TODO: always build in conan v2
        # this is a limitation of conan v1:
        # at build time we want to inject PATH/LD_LIBRARY/DYLD_LIBRARY_PATH
        # of build requirements so that gprc_cpp_plugin can find its
        # shared dependencies (in build context as well)
        # should be fixed by using: CMakeToolchain + VirtualBuildEnv
        if tools.build.cross_building(self, self) and self.options["grpc"].shared:
            return
        with self._buildenv():
            cmake = CMake(self)
            # FIXME: This combination of settings randomly fails in CI
            cmake.definitions["TEST_ACTUAL_SERVER"] = not (self.settings.compiler == "Visual Studio"
                                                           and self.settings.compiler.version == "15"
                                                           and self.settings.build_type == "Release")
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
