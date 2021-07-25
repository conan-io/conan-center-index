import os
from conans import ConanFile, CMake, tools


class GeotransTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    default_options = {"geotrans:shared": True}

    def build(self):
        cmake = CMake(self)
        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is
        # in "test_package"
        cmake.configure()
        cmake.build()

    def imports(self):
        # Import the data files from the package
        # The package will not work without these files
        self.copy("*", dst="data", src="res")

    def test(self):
        if not tools.cross_building(self):
            os.chdir("bin")
            data_loc = "..{sep}data".format(sep=os.sep)
            os.environ["MSPCCS_DATA"] = data_loc
            self.run(".{sep}example".format(sep=os.sep))
