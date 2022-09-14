from conans import ConanFile
import os


class TestPackage(ConanFile):
    settings = "os", "arch"

    test_type = "explicit"
    
    def build_requirements(self):
        self.build_requires(self.tested_reference_str)
        
    def test(self):
        self.run("ninja --version", run_environment=True)
