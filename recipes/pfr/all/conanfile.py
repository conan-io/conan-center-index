from conans import ConanFile, tools
import os


class LibnameConan(ConanFile):
    name = "pfr"
    description = "std::tuple like methods for user defined types without any macro or boilerplate code"
    topics = ("conan", "boost", "pfr", "reflection", "magic_get")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/apolukhin/magic_get"
    license = "BSL-1.0"
    no_copy_source = True
    exports_sources = "BSL-1.0.txt"

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "magic_get-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="BSL-1.0.txt", dst="licenses")
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
