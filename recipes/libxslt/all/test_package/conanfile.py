from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            xml_path = os.path.join(self.source_folder, "example.xml")
            xsl_path = os.path.join(self.source_folder, "example.xsl")
            cmd = "%s %s %s" % (bin_path, xsl_path, xml_path)
            self.run(cmd, run_environment=True)
            self.run("xsltproc -V", run_environment=True)
