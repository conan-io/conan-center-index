from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.microsoft import is_msvc
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    @property
    def _is_legacy_one_profile(self):
        return not hasattr(self, "settings_build")

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)
        self.requires("protobuf/3.21.12")

    def build_requirements(self):
        if not self._is_legacy_one_profile:
            # For the grpc-cpp-plugin executable at build time
            self.tool_requires(self.tested_reference_str)
            self.tool_requires("protobuf/<host_version>")

    def generate(self):
        # Set up environment so that we can run protoc & grpc-cpp-plugin at build time
        if self._is_legacy_one_profile:
            VirtualRunEnv(self).generate(scope="build")
        else:
            VirtualBuildEnv(self).generate()

        # Environment so that the compiled test executable can load shared libraries
        runenv = VirtualRunEnv(self)
        runenv.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["TEST_ACTUAL_SERVER"] = not (is_msvc(self)
                                                        and str(self.settings.compiler.version) in ("15", "191")
                                                        and self.settings.build_type == "Release")

        # Additional logic to override the make program on MacOS if /usr/bin/make is found by CMake
        # which otherwise prevents the propagation of DYLD_LIBRARY_PATH as set by the VirtualBuildEnv
        project_include = os.path.join(self.source_folder, "macos_make_override.cmake")
        tc.cache_variables["CMAKE_PROJECT_test_package_INCLUDE"] = project_include
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
