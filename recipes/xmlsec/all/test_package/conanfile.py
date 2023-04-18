from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["XMLSEC_WITH_XSLT"] = self.dependencies["xmlsec"].options.with_xslt
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            xml_file = os.path.join(self.source_folder, "sign1-tmpl.xml")
            pem_file = os.path.join(self.source_folder, "rsakey.pem")
            self.run(f"{bin_path} {xml_file} {pem_file}", env="conanrun")
