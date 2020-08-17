import os
from conans import ConanFile, tools


class StructoptConan(ConanFile):
    name = "structopt"
    homepage = "https://github.com/p-ranav/structopt"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Parse command line arguments by defining a struct+"
    license = "MIT"
    settings = "compiler", "os"
    topics = ("conan", "structopt", "argument-parser", "cpp17", "header-only",
        "single-header-lib", "header-library", "command-line", "arguments",
        "mit-license", "modern-cpp", "structopt", "lightweight", "reflection",
        "cross-platform", "library", "type-safety", "type-safe", "argparse",
        "clap", "visit-struct-library", "magic-enum")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 17)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="*.h", src=os.path.join(self._source_subfolder, "include"), dst="include")
        self.copy(pattern="*.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        pass
