from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["XMLSEC_WITH_XSLT"] = self.options["xmlsec"].with_xslt
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            xml_file = os.path.join(self.source_folder, os.pardir, "test_package", "sign1-tmpl.xml")
            pem_file = os.path.join(self.source_folder, os.pardir, "test_package", "rsakey.pem")
            self.run(f"{bin_path} {xml_file} {pem_file}", run_environment=True)
