from conans import ConanFile, CMake, tools
from fnmatch import fnmatch
import os


class TlExpectedConan(ConanFile):
    name = "tl-expected"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tl.tartanllama.xyz"
    description = "C++11/14/17 std::expected with functional-style extensions"
    topics = ("cpp11", "cpp14", "cpp17", "expected")
    license = "CC0-1.0"
    no_copy_source = True
    _source_subfolder = "tl-expected"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self._archive_dir, self._source_subfolder)

    @property
    def _archive_dir(self):
        # the archive expands to a directory named expected-[COMMIT SHA1];
        # we'd like to put this under a stable name
        expected_dirs = [
            de for de in os.scandir(self.source_folder)
            if de.is_dir() and fnmatch(de.name, "expected-*")
        ]
        return expected_dirs[0].name

    def package(self):
        self.copy("*",
                  src=os.path.join(self._source_subfolder, "include"),
                  dst="include")
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "tl-expected"
        self.cpp_info.names["cmake_find_package_multi"] = "tl-expected"
        self.cpp_info.components["expected"].name = "expected"
