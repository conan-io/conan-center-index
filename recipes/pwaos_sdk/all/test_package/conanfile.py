import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout

required_conan_version = ">=1.50.0"


class PwaosSdkTestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        # Explicit traits: pwaos_sdk ships the C ABI header + client library;
        # consumers compile and link against them. Without this, application-
        # typed packages get headers=False/libs=False defaults and CMakeDeps
        # would generate a target without include dirs or libraries.
        self.requires(self.tested_reference_str, headers=True, libs=True, run=True)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            # Link/ABI smoke by default. The full hello runtime flow (spawn
            # pwaos_server) additionally runs when the environment has a
            # display; extra client args are forwarded to the server
            # (e.g. --no-sandbox on root/CI).
            bin_path = self.cpp.build.bindirs[0]
            extra = os.environ.get("PWAOS_TEST_ARGS", "")
            if hasattr(os, "getuid") and os.getuid() == 0:
                # Chromium-based servers refuse to run as root without it.
                extra = (extra + " --no-sandbox").strip()
            self.run((os.path.join(bin_path, "test_package") + " " + extra).strip(),
                     env="conanrun")
