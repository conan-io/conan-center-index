import os
import re
from io import StringIO

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        # when --static-linked-ext is used, ruby defines EXTSTATIC as 1
        # But when ruby itself is static there's nothing, so:
        # We define RUBY_STATIC_RUBY when ruby itself is static
        # We define RUBY_STATIC_LINKED_EXT when the ruby extensions are static (same as EXTSTATIC but clearer)
        # This is only for testing purposes
        ruby_opts = self.dependencies[self.tested_reference_str].options
        tc = CMakeToolchain(self)
        tc.variables["RUBY_STATIC_RUBY"] = not ruby_opts.shared
        tc.variables["RUBY_STATIC_LINKED_EXT"] = not ruby_opts.shared and ruby_opts.with_static_linked_ext
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _ruby_version(self):
        tokens = re.split("[@#]", self.tested_reference_str)
        return tokens[0].split("/", 1)[1]

    def _test_ruby_executable_version(self):
        # test executable
        output = StringIO()
        self.run("ruby --version", output, env="conanbuild")
        output_str = str(output.getvalue()).strip()
        self.output.info(f"Installed version: {output_str}")
        assert_ruby_version = f"ruby {self._ruby_version()}"
        self.output.info(f"Expected version: {assert_ruby_version}")
        assert assert_ruby_version in output_str

    def _test_ruby_execute(self):
        # test executable
        output = StringIO()
        self.run('ruby -e "puts RUBY_VERSION"', output, env="conanbuild")
        output_str = str(output.getvalue()).strip()
        self.output.info(f'ruby -e "puts RUBY_VERSION": "{output_str}"')
        assert_ruby_version = self._ruby_version()
        self.output.info(f"Expected version: '{assert_ruby_version}'")
        assert assert_ruby_version in output_str

    def test(self):
        self._test_ruby_executable_version()
        self._test_ruby_execute()

        if can_run(self):
            # test library
            bin_path = os.path.join(self.cpp.build.bindirs[0], "bin", "test_package")
            self.run(bin_path, env="conanrun")
