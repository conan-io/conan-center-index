import os
from conans import ConanFile, tools


class SjsonCppConan(ConanFile):
    name = "sjson-cpp"
    description = "An Simplified JSON (SJSON) C++ reader and writer"
    topics = ("json", "sjson", "simplified")
    license = "MIT"
    homepage = "https://github.com/nfrechette/sjson-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "includes"))

    def package_id(self):
        self.info.header_only()
