import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conans.tools import Version

class Tabulate(ConanFile):
    name = "tabulate"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/p-ranav/tabulate"
    description = "Table Maker for Modern C++"
    settings = "compiler"
    topics = ("header-only", "cpp17", "tabulate", "table", "cli")
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        compiler = str(self.settings.compiler)
        compiler_version = tools.scm.Version(self.settings.compiler.version)

        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, "17")
        else:
            self.output.warn("%s recipe lacks information about the %s compiler"
                             " standard version support" % (self.name, compiler))

        minimal_version = {
            "Visual Studio": "16",
            "gcc": "7.3",
            "clang": "6",
            "apple-clang": "10.0"
        }

        if compiler not in minimal_version:
            self.output.info("%s requires a compiler that supports at least"
                             " C++17" % self.name)
            return

        if compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports"
                                            " at least C++17. %s %s is not"
                                            " supported." % (self.name, compiler, Version(self.settings.compiler.version)))

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
