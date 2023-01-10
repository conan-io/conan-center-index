import os

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conans.client.tools import which
from conans.errors import ConanException


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["FLEX_ROOT"] = self.dependencies[self.tested_reference_str].package_folder
        tc.generate()

    def build(self):
        if not hasattr(self, "settings_build"):
            # Only test location of flex executable when not cross building
            flex_bin = which("flex")

            if not flex_bin.startswith(self.dependencies[self.tested_reference_str].package_folder):
                raise ConanException("Wrong flex executable captured")

        if not cross_building(self, skip_x64_x86=True) or hasattr(self, "settings_build"):
            output_file = os.path.join(self.folders.build_folder, "basic_nr.cpp")
            source_file = os.path.join(self.source_folder, "basic_nr.l")
            self.run(f"flex --outfile={output_file} --c++ {source_file}", run_environment=not hasattr(self, "settings_build"))
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not cross_building(self, skip_x64_x86=True):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            src = os.path.join(self.source_folder, "basic_nr.txt")
            self.run("{} {}".format(bin_path, src), run_environment=True)
            test_yywrap = os.path.join(self.folders.build_folder, "test_yywrap")
            self.run(test_yywrap, run_environment=True)
