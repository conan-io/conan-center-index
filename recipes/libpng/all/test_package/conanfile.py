from conan import ConanFile, tools
from conans import CMake
import os
import re
import subprocess


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            if "arm" in self.settings.arch and not tools.os_info.is_macos:
                self.test_arm()
            else:
                bin_path = os.path.join("bin", "test_package")
                self.run(bin_path, run_environment=True)

    def test_arm(self):
        file_ext = "so" if self.options["libpng"].shared else "a"
        lib_path = os.path.join(self.deps_cpp_info["libpng"].libdirs[0], "libpng.%s" % file_ext)
        output = subprocess.check_output(["readelf", "-h", lib_path]).decode()
        assert re.search(r"Machine:\s+ARM", output)
