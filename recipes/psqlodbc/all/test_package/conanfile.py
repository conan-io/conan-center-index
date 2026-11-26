from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _module_path(self, module_name):
        # libtool builds these as loadable modules (-module), which always get
        # the .so extension, even on Macos.
        dep = self.dependencies[self.tested_reference_str]
        return os.path.join(dep.package_folder, dep.cpp_info.libdirs[0], module_name + ".so")

    def test(self):
        if can_run(self):
            exe = os.path.join(self.cpp.build.bindirs[0], "test_package")
            for module_name in ("psqlodbcw", "psqlodbca"):
                module_path = self._module_path(module_name)
                self.run(f'"{exe}" "{module_path}"', env="conanrun")
