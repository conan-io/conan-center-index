from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class Crc_CppConan(ConanFile):
    name = "crc_cpp"
    description = "A header only, constexpr / compile time small-table based CRC library for C++17 or newer"
    topics = ("conan", "crc_cpp", "crc", "constexpr" "cpp17", "cpp20", "header-only")
    settings = "compiler", "os"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AshleyRoll/crc_cpp"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
       tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")

