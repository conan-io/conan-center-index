from conan import ConanFile, conan_version
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
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
            gdal_options = self.options["gdal"] if conan_version < "2" else self.dependencies["gdal"].options
            if gdal_options.tools:
                self.run("gdal_translate --formats", env="conanrun")
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
            bin_path_c = os.path.join(self.cpp.build.bindirs[0], "test_package_c")
            self.run(bin_path_c, env="conanrun")
