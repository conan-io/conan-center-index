from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["USE_SHARED"] = self.options["libjpeg-turbo"].shared
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            img_name = os.path.join(self.source_folder, "testimg.jpg")
            bin_path = os.path.join("bin", "test_package")
            self.run('%s %s' % (bin_path, img_name), run_environment=True)
