from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    def build(self):
        cmake = CMake(self)
        cmake.definitions["protobuf_VERBOSE"] = True
        cmake.definitions["protobuf_MODULE_COMPATIBLE"] = True
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("protoc --version", run_environment=True)
