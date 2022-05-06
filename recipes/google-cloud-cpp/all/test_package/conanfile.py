from conans import ConanFile, CMake, tools
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run("{} bucket_name".format(os.path.join("bin", "storage")), run_environment=True)
            self.run("{} project_id topic_id".format(os.path.join("bin", "pubsub")), run_environment=True)
