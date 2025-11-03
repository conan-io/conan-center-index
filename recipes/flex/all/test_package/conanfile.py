import os
import re
from io import StringIO

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout, CMakeDeps, CMakeToolchain


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def layout(self):
        cmake_layout(self)

    def _assert_expected_version(self):
        def tested_reference_version():
            tokens = re.split('[@#]', self.tested_reference_str)
            return tokens[0].split("/", 1)[1]

        output = StringIO()
        self.run(f"flex --version", output, env="conanrun")
        output_str = str(output.getvalue())
        self.output.info("Installed version: {}".format(output_str))
        expected_version = tested_reference_version()
        self.output.info("Expected version: {}".format(expected_version))
        assert_flex_version = "flex {}".format(expected_version)
        assert(assert_flex_version in output_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["FLEX_EXECUTABLE"] = os.path.join(self.dependencies["flex"].cpp_info.bindir, "flex")
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self._assert_expected_version()
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            txt_file = os.path.join(self.source_folder, "basic_nr.txt")
            self.run(f"{bin_path} {txt_file}", env="conanrun")
