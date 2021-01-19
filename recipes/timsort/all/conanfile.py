import os

from conans import ConanFile, tools

required_conan_version = ">=1.32.0"

class TimsortConan(ConanFile):
    name = "timsort"
    description = "A C++ implementation of timsort"
    topics = "conan", "timsort", "sorting", "algorithms"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/timsort/cpp-TimSort"
    license = "MIT"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.cppstd:
            if tools.Version(self.version) >= "2.0.0":
                tools.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "cpp-TimSort-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "gfx-timsort"
        self.cpp_info.filenames["cmake_find_package_multi"] = "gfx-timsort"
        self.cpp_info.names["cmake_find_package"] = "gfx"
        self.cpp_info.names["cmake_find_package_multi"] = "gfx"
        self.cpp_info.components["gfx-timsort"].names["cmake_find_package"] = "timsort"
        self.cpp_info.components["gfx-timsort"].names["cmake_find_package_multi"] = "timsort"
