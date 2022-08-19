from conans import ConanFile, CMake, tools


class LibhalTestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ("cmake_find_package", "cmake_paths")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run("./test_package")
