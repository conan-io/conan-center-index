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
            arg_path1 = os.path.abspath(os.path.join(os.path.dirname(__file__), "sign1-tmpl.xml"))
            arg_path2 = os.path.abspath(os.path.join(os.path.dirname(__file__), "rsakey.pem"))
            bin_arg_path = "%s %s %s" % (bin_path, arg_path1, arg_path2)
            self.run(bin_arg_path, run_environment=True)
