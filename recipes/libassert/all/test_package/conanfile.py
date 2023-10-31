from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.files import copy
from conan.tools.scm import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        if Version(self.dependencies["libassert"].ref.version) < Version("1.2.1"):
            for dep in self.dependencies.values():
                copy(self, "*.dll", dep.cpp_info.libdirs[0], self.build_folder)

    def build(self):
        variables = {}
        if Version(self.dependencies["libassert"].ref.version) < Version("1.2.1"):
            variables["CONAN_ASSERT_ASSERT_ASSERT"] = True
        cmake = CMake(self)
        cmake.configure(variables=variables)
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
