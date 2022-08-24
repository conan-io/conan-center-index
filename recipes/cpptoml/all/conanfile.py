from conan import ConanFile, tools
import os


class CppTomlConan(ConanFile):
    name = "cpptoml"
    description = "cpptoml is a header-only library for parsing TOML "
    topics = ("toml", "header-only", "configuration")
    license = "MIT"
    homepage = "https://github.com/skystrife/cpptoml"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()
