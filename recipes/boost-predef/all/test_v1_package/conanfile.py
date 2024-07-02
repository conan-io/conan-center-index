from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    def build(self):
        # FIXME: tools.vcvars added for clang-cl. Remove once conan supports clang-cl properly. (https://github.com/conan-io/conan-center-index/pull/1453)
        with tools.vcvars(self.settings) if (self.settings.os == "Windows" and self.settings.compiler == "clang") else tools.no_op():
            cmake = CMake(self)
            cmake.configure()
            # Disable parallel builds because c3i (=conan-center's test/build infrastructure) seems to choke here
            cmake.parallel = False
            cmake.build()

    def test(self):
        if tools.cross_building(self):
            return
        self.run(f"ctest --output-on-failure -C {self.settings.build_type}", run_environment=True)

