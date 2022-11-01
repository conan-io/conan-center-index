from conans import ConanFile, tools
import os
import shutil

class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _cppfront_input_path(self):
        return os.path.join(self.build_folder, "pure2-hello.cpp2")

    def build(self):
        if not tools.cross_building(self):
            shutil.copy2(src=os.path.join(self.source_folder, "..", "test_package", "pure2-hello.cpp2"), dst=os.path.join(self.build_folder, "pure2-hello.cpp2"))
            self.run("cppfront {}".format(os.path.join(self.build_folder, "pure2-hello.cpp2")), run_environment=True)

    def test(self):
        if not tools.cross_building(self):
            self.run("cppfront -h", run_environment=True)
            assert os.path.isfile(os.path.join(self.build_folder, "pure2-hello.cpp"))
