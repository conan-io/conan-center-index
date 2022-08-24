from conan import ConanFile, tools$
import os

required_conan_version = ">=1.36.0"


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not tools.build.cross_building(self, self):
            src = os.path.join(self.source_folder, "test_package.c")
            self.run("makedepend -f- -- -- {}".format(src), run_environment=True)
