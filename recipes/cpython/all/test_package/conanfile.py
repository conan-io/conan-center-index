from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain
from conan.tools.scm import Version
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.microsoft import is_msvc

import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        #py_version = Version(self.deps_cpp_info["cpython"].version)
        py_version = Version("3.10.4")
        cmake_layout(self, src_folder=f"py{py_version.major}")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_MODULE"] = not is_msvc(self) or self.options["cpython"].shared
        tc.generate()

        vb = VirtualBuildEnv(self)
        vb.generate(scope="build")

        if can_run(self):
            vr = VirtualRunEnv(self)
            vr.generate(scope="run")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
