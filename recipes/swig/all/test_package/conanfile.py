from conans import CMake, ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        if self.settings.compiler != "Visual Studio":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
            cmake.test(output_on_failure=True)

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("swig -version")
