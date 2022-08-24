from conan import ConanFile, tools
from conans import CMake
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    @property
    def _extra_flags(self):
        return self.deps_user_info["platform.hashing"].suggested_flags

    def build(self):
        if self.settings.compiler != "Visual Studio":
            if not self._extra_flags:
                raise ConanException("Suggested flags are not available for os={}/arch={}".format(self.settings.os, self.settings.arch))

        cmake = CMake(self)
        if self.settings.compiler != "Visual Studio":
            cmake.definitions["EXTRA_FLAGS"] = self._extra_flags
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
