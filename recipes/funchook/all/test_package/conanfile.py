import os
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    _cmake = None

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            # Funchook author reports hooking on x86_64 MacOS *can* work but only in shared libs
            #    as I don't have an easy way to still test this, I have skipped the tests for MacOS
            if self.settings.os != "Macos":
                bin_path = os.path.join("bin", "test_package")
                self.run(bin_path, run_environment=True)
