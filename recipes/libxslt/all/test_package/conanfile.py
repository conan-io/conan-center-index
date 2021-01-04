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
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "libxslt_tutorial")
            xml_path = os.path.join(self.source_folder, "example.xml")
            xsl_path = os.path.join(self.source_folder, "example.xsl")
            cmd = "%s %s %s" % (bin_path, xsl_path, xml_path)
            self.run(cmd, run_environment=True)
