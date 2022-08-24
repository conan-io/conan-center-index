from conan import ConanFile, tools
from conans import CMake
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"

    def build(self):
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self, skip_x64_x86=True):
            self.run("pexports -H", run_environment=True)
            if self.settings.os == "Windows":
                bin_path = os.path.join("bin", "test_package")
                self.run(bin_path, run_environment=True)
                exports_def_path = os.path.join(self.build_folder, "exports.def")
                exports_def_contents = tools.files.load(self, exports_def_path)
                self.output.info("{} contents:\n{}".format(exports_def_path, exports_def_contents))
                if not "test_package_function" in exports_def_contents:
                    raise ConanException("pexport could not detect `test_package_function` in the dll")
