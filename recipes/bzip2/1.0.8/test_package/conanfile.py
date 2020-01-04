import os
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake", "pkg_config"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        assert os.path.isfile(os.path.join(self.deps_cpp_info["bzip2"].rootpath, "licenses", "LICENSE"))
        assert os.path.isfile(os.path.join(self.build_folder, "bzip2.pc"))
        if tools.cross_building(self.settings):
            self.output.warn("Skipping run cross built package")
            return

        bin_path = os.path.join("bin", "test_package")
        self.run("%s --help" % bin_path, run_environment=True)
