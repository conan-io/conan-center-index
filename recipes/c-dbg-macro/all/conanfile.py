from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


required_conan_version = ">=1.33.0"

class DbgMacroConan(ConanFile):
    name = "c-dbg-macro"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eerimoq/dbg-macro"
    license = "MIT"
    description = "A dbg(...) macro for C"
    topics = ("conan", "debugging", "macro", "pretty-printing", "header-only")
    settings = ("compiler",  "build_type", "os", "arch")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("This library is not compatible with Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("include/dbg.h", dst=".", src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
