import os
from conan import ConanFile, tools


required_conan_version = ">=1.46.0"

class ClippConan(ConanFile):
    name = "clipp"
    description = """Easy to use, powerful & expressive command line argument parsing for modern C++ / single header / usage & doc generation."""
    topics = ("clipp", "argparse", "cli", "usage", "options", "subcommands")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/muellan/clipp"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        tools.files.copy(self, pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        tools.files.copy(self, pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()
