from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import glob
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
        dependency = self.dependencies["llhttp"]
        shared_libraries = [
            path
            for folder in ("lib", "bin")
            for pattern in ("*.so*", "*.dylib", "*.dll")
            for path in glob.glob(os.path.join(dependency.package_folder, folder, pattern))
        ]
        if bool(dependency.options.shared) != bool(shared_libraries):
            raise ConanException("Packaged library type does not match the shared option")
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
