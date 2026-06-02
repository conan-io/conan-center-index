from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        lz4 = self.dependencies["lz4"]
        tc = CMakeToolchain(self)
        tc.variables["TEST_SHARED_LIB"] = lz4.options.get_safe("fPIC", True)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")

            if self.dependencies["lz4"].options.with_cli:
                with open("file.txt", "w", encoding="utf-8") as f:
                    f.write("Hello Conan world")
                self.run("lz4 file.txt",        env="conanrun")
                self.run("lz4cat file.txt.lz4", env="conanrun")

