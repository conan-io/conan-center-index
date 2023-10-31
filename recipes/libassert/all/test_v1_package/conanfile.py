from conans import ConanFile, CMake
from conan.tools.build import cross_building
from conan.tools.scm import Version
import os
import re

# legacy validation with Conan 1.x
class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        variables = {}
        require_version = re.split('[@#]', self.tested_reference_str)[0].split("/", 1)[1]
        if Version(require_version) < Version("1.2.1"):
            variables["CONAN_ASSERT_ASSERT_ASSERT"] = True
        cmake = CMake(self)
        cmake.configure(defs=variables)
        cmake.build()

    def imports(self):
        require_version = re.split('[@#]', self.tested_reference_str)[0].split("/", 1)[1]
        if Version(require_version) < Version("1.2.1"):
            self.copy("*.dll", dst="bin", src="lib")

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
