from conans import ConanFile, CMake, tools
from io import StringIO
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            config_path = os.path.join(self.source_folder, os.pardir, "test_package", "hello.conf")
            output = StringIO()
            self.run(f"{bin_path} {config_path}", run_environment=True, output=output)
            text = output.getvalue()
            print(text)
            assert "Neighbour" in text
