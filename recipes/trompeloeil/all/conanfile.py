from conan import ConanFile, tools$
import os

required_conan_version = ">=1.33.0"

class TrompeloeilConan(ConanFile):
    name = "trompeloeil"
    description = "Header only C++14 mocking framework"
    topics = ("trompeloeil", "header-only", "mocking")
    homepage = "https://github.com/rollbear/trompeloeil"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0"
    settings = "os", "compiler", "build_type", "arch"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="LICENSE*.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
