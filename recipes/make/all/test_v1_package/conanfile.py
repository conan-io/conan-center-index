from conans import ConanFile, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not tools.cross_building(self):
            with tools.run_environment(self):
                make = self.deps_user_info["make"].make
                makefile_dir = os.path.join(self.source_folder, os.pardir, "test_package")
                self.run(f"{make} -C {makefile_dir} love")
