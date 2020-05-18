from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class BitserializerConan(ConanFile):
    name = "bitserializer"
    description = "Core part of C++ 17 library for serialization to JSON, XML, YAML"
    topics = ("serialization", "json", "xml")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://bitbucket.org/Pavel_Kisliak/bitserializer"
    license = "MIT"
    settings = ("compiler",)
    no_copy_source = True

    @property
    def _supported_compilers(self):
        return {
            "gcc": "8",
            "clang": "7",
            "Visual Studio": "15",
            "apple-clang": "10",
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "17")
        try:
            minimum_required_compiler_version = self._supported_compilers[str(self.settings.compiler)]
            if tools.Version(self.settings.compiler.version) < minimum_required_compiler_version:
                raise ConanInvalidConfiguration("This package requires c++17 support. The current compiler does not support it.")
        except KeyError:
            self.output.warn("This recipe has no support for the current compiler. Please consider adding it.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        # Find and rename folder in the extracted sources
        # This workaround used in connection that zip-archive from BitBucket contains folder with some hash in name
        for dirname in os.listdir(self.source_folder):
            if "-bitserializer-" in dirname:
                os.rename(dirname, self._source_subfolder)
                break

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "core")
        self.copy(pattern="license.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
