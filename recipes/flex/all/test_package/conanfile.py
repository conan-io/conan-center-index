from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            self.run("flex --version", run_environment=True)

            flex_bin = tools.which("flex")
            if not flex_bin.startswith(self.deps_cpp_info["flex"].rootpath):
                raise ConanException("Wrong flex executable captured")
            cmake = CMake(self)
            cmake.definitions["FLEX_ROOT"] = self.deps_cpp_info["flex"].rootpath
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            bin_path = os.path.join("bin", "test_package")
            src = os.path.join(self.source_folder, "basic_nr.txt")
            self.run("{} {}".format(bin_path, src), run_environment=True)
