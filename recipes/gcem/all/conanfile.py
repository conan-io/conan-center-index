from conans import ConanFile, tools
import os


class GcemConan(ConanFile):
    name = "gcem"
    description = "A C++ compile-time math library using generalized " \
                  "constant expressions."
    license = "Apache-2.0"
    topics = ("conan", "gcem", "math", "header-only")
    homepage = "https://github.com/kthohr/gcem"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy(pattern="*", dst="include",
                  src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
