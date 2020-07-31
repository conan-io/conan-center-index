import os
from conans import ConanFile, CMake, tools

class TestZlibConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake", "pkg_config"

    def configure(self):
        del self.settings.compiler.libcxx

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_MINIZIP"] = self.options["zlib"].minizip
        cmake.configure()
        cmake.build()

    def test(self):
        assert os.path.exists(os.path.join(self.deps_cpp_info["zlib"].rootpath, "licenses", "LICENSE"))
        assert os.path.exists(os.path.join(self.build_folder, "zlib.pc"))
        if "x86" in self.settings.arch and not tools.cross_building(self.settings):
            self.run(os.path.join("bin", "test"), run_environment=True)
            if self.options["zlib"].minizip:
                self.run(os.path.join("bin", "test_minizip"), run_environment=True)
