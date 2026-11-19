from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)
        
    @property
    def _tested_poco_modules(self):
        return ["crypto", "util", "net", "netssl", "data_sqlite", "encodings", "jwt", "prometheus"]

    def generate(self):
        tc = CMakeToolchain(self)
        poco_options = self.dependencies["poco"].options
        for option in self._tested_poco_modules:
            tc.cache_variables["TEST_{}".format(option.upper())] = poco_options.get_safe("enable_{}".format(option), False)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.run(os.path.join(self.cpp.build.bindir, "core"), env="conanrun")
            poco_options = self.dependencies["poco"].options
            for option in self._tested_poco_modules:
                if poco_options.get_safe("enable_{}".format(option), False):
                    test_executable = os.path.join(self.cpp.build.bindir, option)
                    self.run(test_executable, env="conanrun")
