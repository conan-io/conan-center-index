from conans import ConanFile, CMake, tools
from contextlib import contextmanager
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @contextmanager
    def _workaround_2profiles(self):
        if hasattr(self, "settings_build"):
            with tools.environment_append(
                {"MSPCCS_DATA": os.path.join(self.deps_cpp_info["geotrans"].rootpath, "res")}
            ):
                yield
        else:
            yield

    def test(self):
        if not tools.cross_building(self):
            with self._workaround_2profiles():
                bin_path = os.path.join("bin", "test_package")
                self.run(bin_path, run_environment=True)
