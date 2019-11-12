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
        if self.settings.compiler == "Visual Studio":
            if not any([self.settings.compiler.cppstd == std for std in ["17", "20"]]):
                raise ConanInvalidConfiguration("nanoRange requires at least c++17")
        elif not any([str(self.settings.compiler.cppstd) == std for std in ["17", "20", "gnu17", "gnu20"]]):
            raise ConanInvalidConfiguration("nanoRange requires at least c++17")
        else:
            supported_compilers = [("gcc", "7"), ("clang", "5"), ("apple-clang", "10"), ("Visual Studio", "15.7")]
            compiler = self.settings.compiler
            version = Version(self.settings.compiler.version)
            if not any(compiler == e[0] and version >= e[1] for e in supported_compilers):
                raise ConanInvalidConfiguration("Your compiler does not support c++17")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def package(self):
        sourceSubfolder="NanoRange-{}".format( self.conan_data["sources"][self.version]["url"].split("/")[-1][:-7])
        self.copy("*.hpp", src="{}/include".format(sourceSubfolder), dst="include" )
        self.copy("LICENSE_1_0.txt", src=sourceSubfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()
