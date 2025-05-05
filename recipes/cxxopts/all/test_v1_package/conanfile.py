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
            output = StringIO()
            bin_path = os.path.join("bin", "test_package")
            option_string = "-f 41 --bar baria --baz"
            if self.options["cxxopts"].unicode:
                option_string += " -q quxis"
            self.run(f"{bin_path} {option_string}", run_environment=True, output=output)
            output_lines = set(output.getvalue().splitlines())
            expected_lines = {"foo:41", "bar:baria", "baz:1"}
            if self.options["cxxopts"].unicode:
                expected_lines.add("qux:quxis")
            assert(expected_lines.issubset(output_lines))
