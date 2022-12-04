from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.files import replace_in_file
from conan.tools.scm import Version
import os


class TestSpixConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def _patch_sources(self):
        if Version(self.deps_cpp_info["qt"].version).major == 6:
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "cxx_std_14", "cxx_std_17")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_spix")
            self.run(bin_path, env="conanrun")
