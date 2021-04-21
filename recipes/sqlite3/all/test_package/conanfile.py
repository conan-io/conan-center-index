from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        if not self.options["sqlite3"].enable_default_vfs:
            # Need to provide custom VFS code: https://www.sqlite.org/custombuild.html
            return

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not self.options["sqlite3"].enable_default_vfs:
            # That code will not build
            return

        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
