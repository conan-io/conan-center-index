from conans import ConanFile, tools
import os


class DateConan(ConanFile):
    description = "A date and time library based on the C++11/14/17 <chrono> header"
    name = "date"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://howardhinnant.github.io/date/date.html"
    license = "MIT"
    repo_url = "https://www.github.com/HowardHinnant/date"
    topics = ("date", "chrono")
    generators = "cmake"
    no_copy_source = True
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        pass

    def package(self):
        self.copy("*date.h", src=self._source_subfolder)
        self.copy("*LICENSE.txt", dst="licenses", keep_path=False)
