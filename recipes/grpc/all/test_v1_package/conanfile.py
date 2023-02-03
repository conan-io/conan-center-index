from conans import ConanFile, CMake, tools
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
        if tools.cross_building(self):
            yield
        else:
            with tools.run_environment(self):
                yield

    @property
    def macos_grpc_shared(self):
        # Due to SIP limitations on newer macOS, `DYLD_LIBRARY_PATH`, which is set
        # by `tools.run_environment`, will not be propagated properly, see
        # https://stackoverflow.com/questions/35568122/why-isnt-dyld-library-path-being-propagated-here 
        return self.settings.os == "Macos" and self.options["grpc"].shared

    def build(self):
        # TODO: always build in conan v2
        # this is a limitation of conan v1:
        # at build time we want to inject PATH/LD_LIBRARY/DYLD_LIBRARY_PATH
        # of build requirements so that gprc_cpp_plugin can find its
        # shared dependencies (in build context as well)
        # should be fixed by using: CMakeToolchain + VirtualBuildEnv
        if (tools.cross_building(self) and self.options["grpc"].shared) or self.macos_grpc_shared:
            self.output.warning("Skipping build of test_package due to limitation propagating "
                                "runtime environment when invoking protoc and grpc_cpp_plugin. "
                                "For a working example, please see the newer Conan 2.0 compatible "
                                "test package.")
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
        if not tools.cross_building(self) and not self.macos_grpc_shared:
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
