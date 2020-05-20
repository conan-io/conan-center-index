import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version

class SpyConan(ConanFile):
    name = "spy"
    settings = "compiler"
    version = "0.0.3"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://jfalcou.github.io/spy/"
    description = "C++ 17 for constexpr-proof detection and classification of informations about OS, compiler, etc..."
    topics = ("c++17", "config", "metaprogramming")
    no_copy_source = True

    _source_subfolder = "source_subfolder"

    def _supports_cpp17(self):
        supported_compilers = [("gcc", "7"), ("clang", "5"), ("apple-clang", "10"), ("Visual Studio", "15.7")]
        compiler = self.settings.compiler
        version = Version(self.settings.compiler.version)
        return any(compiler == e[0] and version >= e[1] for e in supported_compilers)

    def configure(self):
        if not self._supports_cpp17():
            raise ConanInvalidConfiguration("Spy requires C++17 support")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
