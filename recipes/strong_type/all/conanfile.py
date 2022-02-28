from conans import ConanFile, tools
import os


class StrongtypeConan(ConanFile):
    name = "strong_type"
    license = "MIT"
    description = "Create new type from existing type without changing the interface."
    topics = ("strong_type", "safety")
    homepage = "https://github.com/Enhex/strong_type"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
       tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()
