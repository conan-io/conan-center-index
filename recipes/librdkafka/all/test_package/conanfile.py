import os

from conans import CMake, ConanFile, tools


class LibrdkafkaTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_ZLIB"] = self.options["librdkafka"].zlib
        cmake.definitions["WITH_ZSTD"] = self.options["librdkafka"].zstd
        cmake.definitions["WITH_PLUGINS"] = self.options["librdkafka"].plugins
        cmake.definitions["WITH_SSL"] = self.options["librdkafka"].ssl
        cmake.definitions["WITH_SASL"] = self.options["librdkafka"].sasl
        cmake.definitions["WITH_LZ4"] = self.options["librdkafka"].lz4
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy("*.so*", dst="bin", src="lib")

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "PackageTest")
            self.run(bin_path, run_environment=True)
