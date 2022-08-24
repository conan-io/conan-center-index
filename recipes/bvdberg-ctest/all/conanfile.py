import os
from conans import ConanFile, tools


class BvdbergCtestConan(ConanFile):
    name = "bvdberg-ctest"
    license = "Apache-2.0"
    homepage = "https://github.com/bvdberg/ctest"
    url = "https://github.com/conan-io/conan-center-index"
    description = "ctest is a unit test framework for software written in C."
    topics = ("conan", "testing", "testing-framework", "unit-testing")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "ctest" + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
