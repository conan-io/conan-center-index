from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")

            if self.dependencies["bzip2"].options.build_executable:
                with open("file.txt", "w", encoding="utf-8") as f:
                    f.write("Hello Conan world")
                suffix = ".exe" if self.settings.os == "Windows" else ""
                self.run(f"bzip2{suffix} file.txt", env="conanrun")
                self.run(f"bzcat{suffix} file.txt.bz2", env="conanrun")
