from conans import ConanFile, tools

class ASIOnetConan(ConanFile):
    name = "asionet"
    version = "1.5.0"
    description = "TCP networking framework built on top of asio"
    topics = ("network", "tcp", "async", "parallel")
    exports_sources = "../common/*", "../LICENSE"
    license = "MIT"
    no_copy_source = True
    generators = "premake"
    requires = ("asio/1.18.1", "botan/2.17.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def package(self):
        self.copy("*.hpp", dst="include", excludes="one.hpp")

