import os
from conans import ConanFile, tools
from conan.tools.cmake import CMake
from conan.tools.layout import cmake_layout

class TestZlibConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "PkgConfigDeps"

    def configure(self):
        del self.settings.compiler.libcxx

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def layout(self):
        cmake_layout(self)

    def test(self):
        assert os.path.exists(os.path.join(self.deps_cpp_info["zlib"].rootpath, "licenses", "LICENSE"))
        assert os.path.exists(os.path.join(self.generators_folder, "zlib.pc"))
        if "x86" in self.settings.arch and not tools.cross_building(self.settings):
            # FIXME: Very ugly interface to get the current test executable path
            self.run(os.path.join(self.build_folder, self.cpp.build.libdirs[0], "test"), run_environment=True)
