from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            test_env_dir = "test_env"
            tools.mkdir(test_env_dir)
            bin_path = os.path.join("bin", "test_package")
            handler_exe = "crashpad_handler.exe" if self.settings.os == "Windows" else "crashpad_handler"
            handler_bin_path = os.path.join(self.deps_cpp_info["sentry-crashpad"].rootpath, "bin", handler_exe)
            self.run("%s %s/db %s" % (bin_path, test_env_dir, handler_bin_path), run_environment=True)
