from conan.errors import ConanInvalidConfiguration
from conan import ConanFile, tools

required_conan_version = ">=1.33.0"

class IncbinConan(ConanFile):
    name = "incbin"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Include binary files in C/C++"
    topics = ("include", "binary", "preprocess")
    homepage = "https://github.com/graphitemaster/incbin/"
    no_copy_source = True
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Currently incbin recipe is not supported for Visual Studio because it requires external command 'incbin'.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("UNLICENSE", "licenses", self._source_subfolder)
        self.copy("incbin.h", "include", self._source_subfolder)

    def package_id(self):
        self.info.header_only()
