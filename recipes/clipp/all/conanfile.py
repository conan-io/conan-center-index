import os
import glob
from conan import ConanFile, tools


class ClippConan(ConanFile):
    name = "clipp"
    description = """Easy to use, powerful & expressive command line argument parsing for modern C++ / single header / usage & doc generation."""
    topics = ("conan", "clipp", "argparse")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/muellan/clipp"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
