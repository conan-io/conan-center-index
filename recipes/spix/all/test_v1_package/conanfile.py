from conans import ConanFile, CMake
from conan.tools.build import cross_building
from conan.tools.files import replace_in_file
from conan.tools.scm import Version
import os


class TestSpixV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def _patch_sources(self):
        if Version(self.deps_cpp_info["qt"].version).major == 6:
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "cxx_std_14", "cxx_std_17")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_spix")
            self.run(bin_path, run_environment=True)
