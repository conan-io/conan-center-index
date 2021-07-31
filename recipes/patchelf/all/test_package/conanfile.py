from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            patchelf = os.path.join(self.deps_cpp_info["patchelf"].bin_paths[0], "patchelf")
            self.run("{} --version".format(patchelf), run_environment=True)
