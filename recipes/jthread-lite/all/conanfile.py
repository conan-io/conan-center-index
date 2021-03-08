import os
from conans import ConanFile, tools

required_conan_version = ">=1.28.0"

class JthreadLiteConan(ConanFile):
    name = "jthread-lite"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/jthread-lite"
    description = "jthread lite - C++20's jthread for C++11 and later in a single-file header-only library "
    topics = ("conan", "jthread-lite", "jthread", "cpp11")
    settings = "os"
    license = "BSL-1.0"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "jthread-lite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "jthread-lite"
        self.cpp_info.names["cmake_find_package"] = "nonstd"
        self.cpp_info.names["cmake_find_package_multi"] = "nonstd"
        self.cpp_info.components["jthreadlite"].names["cmake_find_package"] = "jthread-lite"
        self.cpp_info.components["jthreadlite"].names["cmake_find_package_multi"] = "jthread-lite"
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["jthreadlite"].system_libs = ["pthread"]
