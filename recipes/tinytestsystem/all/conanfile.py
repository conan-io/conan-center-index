import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

class TinyTestConan(ConanFile):
    name = "tinytestsystem"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://jfalcou.github.io/tts/"
    description = "C++ 20 unit tests library focusing on numerical testing and extensibility."
    topics = ("c++20", "test", "computing")
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10.2",
            "Visual Studio": "16.27",
            "clang": "10"
        }

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 20)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("TTS requires C++20, which your compiler does not support.")
        else:
            self.output.warn("TTS requires C++20. Your compiler is unknown. Assuming it supports C++20.")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "tts-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst= "include", src=os.path.join(self._source_subfolder, "include"))
