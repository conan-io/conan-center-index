import os
from conans import ConanFile, tools
from conan.tools.cmake import CMake
from conan.tools.layout import cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def configure(self):
        del self.settings.compiler.libcxx

    def layout(self):
        cmake_layout(self)

    def test(self):
        if not tools.cross_building(self.settings):
            # FIXME: Very ugly interface to get the current test executable path
            cmd = os.path.join(self.build_folder, self.cpp.build.bindirs[0], "test_package")
            self.run("%s --help" % cmd, env=["conanrunenv"])
