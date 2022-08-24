import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration


class DbgMacroConan(ConanFile):
    name = "dbg-macro"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sharkdp/dbg-macro"
    license = "MIT"
    description = "A dbg(...) macro for C++"
    topics = ("conan", "debugging", "macro", "pretty-printing", "header-only")
    settings = ("compiler", )
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        minimal_cpp_standard = "11"
        if self.settings.get_safe("compiler.cppstd"):
            tools.build.check_min_cppstd(self, minimal_cpp_standard)

        if self.settings.compiler == "gcc" and tools.scm.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(
                "dbg-mcro can't be used by {0} {1}".format(
                    self.settings.compiler,
                    self.settings.compiler.version
                )
            )

    def package(self):
        self.copy("dbg.h", dst="include", src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
