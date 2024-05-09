from conans import ConanFile, CMake, tools
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
            for exe in ["gettext", "ngettext", "msgcat", "msgmerge", "msgfmt"]:
                self.run(f"{exe} --version", run_environment=True)
            self.run(os.path.join("bin", "test_package"), run_environment=True)
