import os
import re
from io import StringIO

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv", "VirtualBuildEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        # test we can consume wayland scanner as a build requirement
        self.tool_requires(self.tested_reference_str)

        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[2.2 <3]")

    def layout(self):
        cmake_layout(self)

    @property
    def _has_libraries(self):
        return self.dependencies["wayland"].options.get_safe("enable_libraries")

    def _assert_expected_version(self, actual_version):
        def tested_reference_version():
            tokens = re.split('[@#]', self.tested_reference_str)
            return tokens[0].split("/", 1)[1]

        assert tested_reference_version() == actual_version

    def _test_wayland_scanner(self, env):
        buffer = StringIO()
        self.run(f"wayland-scanner --version", env=env, stderr=buffer)
        output = buffer.getvalue().strip()
        self.output.info(f"Wayland scanner output: {output}")
        actual_version = output.split()[-1]
        self._assert_expected_version(actual_version)

    def build(self):
        if self._has_libraries:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

        self._test_wayland_scanner(env="conanbuild")

    def test(self):
        if can_run(self):
            if self._has_libraries:
                bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
                self.run(bin_path, env="conanrun")

            self._test_wayland_scanner(env="conanrun")
