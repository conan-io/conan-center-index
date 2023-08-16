from conans import ConanFile, CMake
from conan.tools.build import cross_building
from conan.tools.files import mkdir
from conan.tools.scm import Version
import os


class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["HAS_PROXY"] = Version(self.deps_cpp_info["sentry-crashpad"].version) > "0.6.2"
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            test_env_dir = "test_env"
            mkdir(self, test_env_dir)
            bin_path = os.path.join("bin", "test_package")
            handler_exe = "crashpad_handler.exe" if self.settings.os == "Windows" else "crashpad_handler"
            handler_bin_path = os.path.join(self.deps_cpp_info["sentry-crashpad"].rootpath, "bin", handler_exe)
            self.run(f"{bin_path} {test_env_dir} {handler_bin_path}", run_environment=True)
