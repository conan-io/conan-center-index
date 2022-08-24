import os
from conan import ConanFile, tools


class BlazeConan(ConanFile):
    name = "blaze"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://bitbucket.org/blaze-lib/blaze"
    description = "open-source, high-performance C++ math library for dense and sparse arithmetic"
    topics = ("conan", "blaze", "math", "algebra", "linear algebra", "high-performance")
    license = "BSD-3-Clause"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("blaze-{}".format(self.version), self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy("LICENSE", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        self.copy(pattern="blaze/*.h", src=os.path.join(self.source_folder, self._source_subfolder), dst="include")
