from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            xml_path = os.path.join(self.source_folder, "books.xml")
            bin_arg_path = "%s %s" % (bin_path, xml_path)
            self.run(bin_arg_path, run_environment=True)
