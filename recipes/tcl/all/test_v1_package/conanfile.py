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
            self.run(bin_path, run_environment=True)
            assert(os.path.exists(os.environ["TCLSH"]))
            self.run("{} {}".format(os.environ["TCLSH"], os.path.join(self.source_folder, "..", "test_package", "hello.tcl")), run_environment=True)
