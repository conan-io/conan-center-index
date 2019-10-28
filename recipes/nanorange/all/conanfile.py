import os

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class NanorangeConan(ConanFile):
    name = "nanorange"
    version = "20191001"
    license = "Boost 1.0"
    author = "Paul M. Bendixen paulbendixen@gmail.com"
    url = "github.com/conan-io/conan-center-index"
    website = "https://github.com/tcbrindle/NanoRange"
    description = "NanoRange is a C++17 implementation of the C++20 Ranges proposals (formerly the Ranges TS)."
    topics = ("ranges", "C++17", "Ranges TS")
    no_copy_source = True
    settings = "compiler"
    # No settings/options are necessary, this is header only

    def configure(self):
        if not any([str(self.settings.compiler.cppstd) == std for std in ["17", "20", "gnu17", "gnu20"]]):
            raise ConanInvalidConfiguration("nanoRange requires at least c++17")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def package(self):
        sourceSubfolder="NanoRange-{}".format( self.conan_data["sources"][self.version]["url"].split("/")[-1][:-4])
        self.copy("*.hpp", src="{}/include".format(sourceSubfolder), dst="include" )
        self.copy("LICENSE_1_0.txt", src=sourceSubfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()
