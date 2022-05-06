from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.build import cross_building
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            self.run("{} bucket_name".format(os.path.join(".", "storage")), run_environment=True)
            self.run("{} project_id topic_id".format(os.path.join(".", "pubsub")), run_environment=True)
