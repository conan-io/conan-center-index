from conan import ConanFile, tools
import os
import glob


class HedleyConan(ConanFile):
    name = "hedley"
    license = "CC0-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nemequ.github.io/hedley/"
    description = "A C/C++ header to help move #ifdefs out of your code"
    topics = ("header", 'header-only', 'preprocessor', "#ifdef", "cross-platform")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        include_folder = self._source_subfolder
        self.copy(pattern="*.h", dst="include", src=include_folder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
