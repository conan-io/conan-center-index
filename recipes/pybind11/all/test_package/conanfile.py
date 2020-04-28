from conans import ConanFile, CMake, tools
import os
import sys


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["Python_ADDITIONAL_VERSIONS"] = "{}.{}".format(sys.version_info.major,sys.version_info.minor)
        cmake.configure()
        cmake.build()

    @property
    def _python_available(self):
        # FIXME: this can be removed once a python interpreter is available in CCI
        return getattr(sys, "frozen", False)

    def test(self):
        if self._python_available and not tools.cross_building(self.settings):
            self.run("{} {} {}".format(sys.executable,
                                       os.path.join(self.source_folder, "test.py"),
                                       os.path.join(self.build_folder, "lib")), run_environment=True)
