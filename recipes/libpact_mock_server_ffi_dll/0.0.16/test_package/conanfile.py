from conans import ConanFile, CMake, tools

class CbindgentestTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    requires = "openssl/1.1.1d"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            with tools.run_environment(self):
                cmake = CMake(self)
                cmake.test()
