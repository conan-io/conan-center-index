import os
from conans import ConanFile, tools


class ExpectedLite(ConanFile):
    name = "expected-lite"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/expected-lite"
    description = "expected lite - Expected objects in C++11 and later in a single-file header-only library"
    topics = ("conan", "cpp11", "cpp14", "cpp17", "expected", "expected-implementations")
    exports_sources = ["patches/**"]
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.info.header_only()
