from conans import ConanFile
import os
import shutil


class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)

    def build(self):
        shutil.copy2(src=os.path.join(self.source_folder, os.pardir, "test_package", "pure2-hello.cpp2"),
                     dst=os.path.join(self.build_folder, "pure2-hello.cpp2"))
        self.run("cppfront {}".format(os.path.join(self.build_folder, "pure2-hello.cpp2")))

    def test(self):
        self.run("cppfront -h")
        assert os.path.isfile(os.path.join(self.build_folder, "pure2-hello.cpp"))
