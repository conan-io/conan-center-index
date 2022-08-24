import os

from conan import ConanFile, tools$

class LestConan(ConanFile):
    name = "lest"
    description = "A modern, C++11-native, single-file header-only, tiny framework for unit-tests, TDD and BDD."
    license = "BSL-1.0"
    topics = ("conan", "testing", "testing-framework", "unit-testing", "header-only")
    homepage = "https://github.com/martinmoene/lest"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()
