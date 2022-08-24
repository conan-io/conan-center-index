from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join(self.deps_cpp_info["objectbox-generator"].rootpath, "bin", "objectbox-generator")
            self.run(bin_path + " -help", run_environment=True)
