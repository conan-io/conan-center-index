from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from io import StringIO
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            output = StringIO()
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            option_string = "-f 41 --bar baria --baz"
            if self.dependencies["cxxopts"].options.unicode:
                option_string += " -q quxis"
            self.run(f"{bin_path} {option_string}", output, env="conanrun")
            output_lines = set(output.getvalue().splitlines())
            expected_lines = {"foo:41", "bar:baria", "baz:1"}
            if self.dependencies["cxxopts"].options.unicode:
                expected_lines.add("qux:quxis")
            assert(expected_lines.issubset(output_lines))
