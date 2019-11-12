import os

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class NanorangeConan(ConanFile):
    name = "nanorange"
    license = "BSL-1.0"
    url = "github.com/conan-io/conan-center-index"
    website = "https://github.com/tcbrindle/NanoRange"
    description = "NanoRange is a C++17 implementation of the C++20 Ranges proposals (formerly the Ranges TS)."
    topics = ("ranges", "C++17", "Ranges TS")
    no_copy_source = True
    settings = "compiler"
    # No settings/options are necessary, this is header only

    def configure(self):
        version = Version( self.settings.compiler.version )
        compiler = self.settings.compiler
        if compiler == "Visual Studio":
            if version < "16":
                raise ConanInvalidConfiguration("NanoRange requires at least Visual Studio version 15.9, please use 16")
            if not any([self.settings.compiler.cppstd == std for std in ["17", "20"]]):
                raise ConanInvalidConfiguration("nanoRange requires at least c++17")
	else:
            if ( compiler == gcc and version < "7" ) or ( compiler == clang and version < "5" ):
                raise ConanInvalidConfiguration("NanoRange requires a compiler that supports at least C++17")
            if compiler == apple-clang:
                self.output.warn("NanoRange is not tested with apple-clang")
                if version < "10":
                    raise ConanInvalidConfiguration("NanoRange requires a compiler that supports at least C++17")
        if not any([str(self.settings.compiler.cppstd) == std for std in ["17", "20", "gnu17", "gnu20"]]):
            raise ConanInvalidConfiguration("nanoRange requires at least c++17")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def package(self):
        sourceSubfolder="NanoRange-{}".format( self.conan_data["sources"][self.version]["url"].split("/")[-1][:-7])
        self.copy("*.hpp", src="{}/include".format(sourceSubfolder), dst="include" )
        self.copy("LICENSE_1_0.txt", src=sourceSubfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()
