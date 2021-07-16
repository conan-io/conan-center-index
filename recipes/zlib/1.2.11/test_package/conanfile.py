import os
from conans import ConanFile, tools
from conan.tools.cmake import CMake
from conan.tools.layout import cmake_layout

class TestZlibConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "PkgConfigDeps", "VirtualRunEnv"

    def configure(self):
        del self.settings.compiler.libcxx

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def layout(self):
        cmake_layout(self)

    def generate(self):
        # Necessary modernization, as test() doesn't have self.dependencies yet.
        assert os.path.exists(os.path.join(self.dependencies["zlib"].package_folder, "licenses", "LICENSE"))

    def test(self):
        assert os.path.exists(os.path.join(self.generators_folder, "zlib.pc"))
        if "x86" in self.settings.arch and not tools.cross_building(self.settings):
            # FIXME: Very ugly interface to get the current test executable path
            cmd = os.path.join(self.build_folder, self.cpp.build.bindirs[0], "test")
            self.output.info("Running {}".format(cmd))
            self.run(cmd, env="conanrunenv")
