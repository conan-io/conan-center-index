from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def layout(self):
        cmake_layout(self)

    def build(self):
        if not hasattr(self, "settings_build"):
            # Only test location of flex executable when not cross building
            flex_bin = shutil.which("flex")
            if not flex_bin.startswith(self.deps_cpp_info["flex"].rootpath):
                raise ConanException("Wrong flex executable captured")

        if not cross_building(self, skip_x64_x86=True) or hasattr(self, "settings_build"):
            self.run("flex --version", run_environment=not hasattr(self, "settings_build"))

            print(os.environ["PATH"])
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not cross_building(self, skip_x64_x86=True):
            bin_path = os.path.join(self.build_folder, "test_package")
            src = os.path.join(self.source_folder, "basic_nr.txt")
            self.run(f"{bin_path} {src}", run_environment=True)

            test_yywrap = os.path.join(self.build_folder, "test_yywrap")
            self.run(test_yywrap, run_environment=True)
