from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        if self.options["magnum-extras"].ui:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            executable_ext = ".exe" if self.settings.os == "Windows" else ""
            if self.options["magnum-extras"].player:
                assert os.path.exists(os.path.join(self.deps_cpp_info["magnum-extras"].rootpath, "bin", "magnum-player{}".format(executable_ext)))
                # (Cannot run in headless mode) self.run("magnum-player --help")
            if self.options["magnum-extras"].ui_gallery:
                assert os.path.exists(os.path.join(self.deps_cpp_info["magnum-extras"].rootpath, "bin", "magnum-ui-gallery{}".format(executable_ext)))
                # (Cannot run in headless mode) self.run("magnum-ui-gallery --help")
            if self.options["magnum-extras"].ui:
                bin_path = os.path.join("bin", "test_package")
                self.run(bin_path, run_environment=True)
