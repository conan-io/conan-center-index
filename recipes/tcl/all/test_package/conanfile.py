from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True, env="conanrun")
            tclsh = self.deps_user_info['tcl'].tclsh
            assert(os.path.exists(tclsh))
            self.run("{} {}".format(tclsh, os.path.join(self.source_folder, "hello.tcl")), run_environment=True, env = "conanrun")
