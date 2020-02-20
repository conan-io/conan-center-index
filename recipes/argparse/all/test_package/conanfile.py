from conans import ConanFile, CMake, tools
from io import StringIO
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            output = StringIO()
            bin_path = os.path.join("bin", "test_package")
            val = 42
            self.run("{} {}".format(bin_path, val), run_environment=True, output=output)
            text = output.getvalue()
            print(text)
            assert(str(val*val) in text)
