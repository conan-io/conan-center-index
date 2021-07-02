from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os


class StduuidConan(ConanFile):
    name = "stduuid"
    description = "A C++17 cross-platform implementation for UUIDs"
    topics = ("conan", "uuid", "guid")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mariusbancila/stduuid"
    license = "MIT"
    settings = "os", "compiler"

    no_copy_source = True
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def requirements(self):
        self.requires("ms-gsl/2.0.0")
        if self.settings.os != "Windows":
            self.requires("libuuid/1.0.3")

    def configure(self):
        version = Version( self.settings.compiler.version )
        compiler = self.settings.compiler
        if self.settings.compiler.cppstd and \
           not any([str(self.settings.compiler.cppstd) == std for std in ["17", "20", "gnu17", "gnu20"]]):
            raise ConanInvalidConfiguration("stduuid requires at least c++17")
        elif compiler == "Visual Studio"and version < "15":
            raise ConanInvalidConfiguration("stduuid requires at least Visual Studio version 15")
        else:
            if ( compiler == "gcc" and version < "7" ) or ( compiler == "clang" and version < "5" ):
                raise ConanInvalidConfiguration("stduuid requires a compiler that supports at least C++17")
            elif compiler == "apple-clang"and version < "10":
                raise ConanInvalidConfiguration("stduuid requires a compiler that supports at least C++17")

    def package(self):
        root_dir = self._source_subfolder
        include_dir = os.path.join(root_dir, "include")
        self.copy(pattern="LICENSE", dst="licenses", src=root_dir)
        self.copy(pattern="uuid.h", dst="include", src=include_dir)

    def package_id(self):
        self.info.header_only()
