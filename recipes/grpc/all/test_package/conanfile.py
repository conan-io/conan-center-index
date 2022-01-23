from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.build_requires(str(self.requires["grpc"]))

    @property
    def _skip_test(self):
        # TODO: remove in conan v2
        # this is a limitation of conan v1:
        # at build time we want to inject PATH/LD_LIBRARY/DYLD_LIBRARY_PATH
        # of build requirements so that gprc_cpp_plugin can find its
        # shared dependencies (in build context as well)
        # should be fixed by using: CMakeToolchain + VirtualBuildEnv
        return tools.cross_building(self) and self.options["grpc"].shared

    def build(self):
        if self._skip_test:
            return
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if self._skip_test:
            return
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
