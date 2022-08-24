from conan import ConanFile, tools
from conans import CMake
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
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            config_path = os.path.join(self.source_folder, "hello.conf")
            output = StringIO()
            self.run("{} {}".format(bin_path, config_path), run_environment=True, output=output)
            text = output.getvalue()
            print(text)
            assert "Neighbour" in text
