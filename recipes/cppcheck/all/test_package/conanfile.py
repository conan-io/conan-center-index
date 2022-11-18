from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.files import copy
import os
import sys

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        copy(self, "file_to_check.cpp", self.source_folder, self.build_folder)
        if can_run(self):
            self.run(f"cppcheck --enable=warning,style,performance --std=c++11 .", env="conanrun")

            # On windows we need to explicitly use python to run the python script
            if self.settings.os == 'Windows':
                self.run("{} {} -h".format(sys.executable, os.getenv("CPPCHECK_HTMLREPORT")), env="conanrun")
            else:
                self.run("cppcheck-htmlreport -h", env="conanrun")
