import os
from conans import ConanFile, tools

required_conan_version = ">=1.28.0"

class RingSpanLiteConan(ConanFile):
    name = "ring-span-lite"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/ring-span-lite"
    description = ("ring-span lite - A ring_span type for C++98, C++11 and later in a \
                    single-file header-only library ")
    topics = ("conan", "cpp98", "cpp11", "cpp14", "cpp17", "ring-span")
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
        self.cpp_info.filenames["cmake_find_package"] = "ring-span-lite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "ring-span-lite"
        self.cpp_info.names["cmake_find_package"] = "nonstd"
        self.cpp_info.names["cmake_find_package_multi"] = "nonstd"
        self.cpp_info.components["ringspanlite"].names["cmake_find_package"] = "ring-span-lite"
        self.cpp_info.components["ringspanlite"].names["cmake_find_package_multi"] = "ring-span-lite"
