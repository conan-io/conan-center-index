from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualRunEnv
import glob
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        CMakeToolchain(self).generate()
        VirtualRunEnv(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _module_path(self, module_name):
        dep = self.dependencies[self.tested_reference_str]
        candidates = []
        for libdir in dep.cpp_info.libdirs:
            if not os.path.isabs(libdir):
                libdir = os.path.join(dep.package_folder, libdir)
            for suffix in (".so", ".dylib", ".bundle"):
                candidates.extend(glob.glob(os.path.join(libdir, module_name + suffix)))
        candidates = sorted(set(candidates))
        assert candidates, f"Could not find {module_name} driver module in {dep.cpp_info.libdirs}"
        return candidates[0]

    def test(self):
        if can_run(self):
            exe = os.path.join(self.cpp.build.bindirs[0], "test_package")
            for module_name in ("psqlodbcw", "psqlodbca"):
                module_path = self._module_path(module_name)
                self.run(f'"{exe}" "{module_path}"', env="conanrun")
