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
            # Download a public domain xm file; https://modarchive.org/module.php?178293
            tools.download(
                "https://api.modarchive.org/downloads.php?moduleid=178293#burbs.xm",
                filename="burbs.xm",
                sha256="ced080401a2635cddc6d13b9095efa217f260ce7b3a482a29b454f72317b0c4d",
                )
            bin_path = os.path.join("bin", "test_package")
            self.run("%s %s" % (bin_path, "burbs.xm"), run_environment=True)
