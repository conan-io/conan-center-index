import io

from conan import ConanFile, conan_version
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _test(self, executable):
        bin_path = os.path.join(self.cpp.build.bindir, executable)
        if conan_version >= "2.0.15":
            stderr = io.StringIO()
            self.run(bin_path, env="conanrun",  stderr=stderr)
            stderr = stderr.getvalue()
            self.output.info(stderr)
            assert "MALLOC: " in stderr, "MALLOCSTATS was not successfully enabled"
        else:
            self.run(bin_path, env="conanrun")

    def test(self):
        if can_run(self):
            os.environ["MALLOCSTATS"] = "1"
            self._test("test_package_indirect")
            self._test("test_package_direct")
