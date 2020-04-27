import os
from conans import ConanFile, tools

class CtreConan(ConanFile):
    name = "ctre"
    homepage = "https://github.com/hanickadot/compile-time-regular-expressions"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Compile Time Regular Expression for C++17/20"
    topics = ("cpp17", "regex", "compile-time-regular-expressions")
    license = "Apache 2.0 with LLVM Exception"
    no_copy_source = True

    _source_name = "compile-time-regular-expressions"
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self._source_name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

