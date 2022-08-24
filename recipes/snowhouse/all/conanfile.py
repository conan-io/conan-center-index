from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class SnowHouseConan(ConanFile):
    name = "snowhouse"
    description = "An assertion library for C++"
    topics = ("assertion", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/banditcpp/snowhouse"
    license = "BSL-1.0"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
       tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE_1_0.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()
