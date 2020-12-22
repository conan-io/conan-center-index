from conans import ConanFile, CMake, tools

class SociTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    requires = ["catch2/2.13.3", "fmt/6.2.0"]

    def requirements(self):
        self.requires("catch2/2.13.3")
        self.requires("fmt/6.2.0")

    def configure(self):
        self.options["soci"].static     = True
        self.options["soci"].cxx11      = True
        self.options["soci"].empty      = True
        self.options["soci"].shared     = True
        self.options["soci"].sqlite3    = True

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run("ctest . -Q")
