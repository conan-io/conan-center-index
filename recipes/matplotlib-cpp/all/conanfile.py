from conans import ConanFile, tools
import os
import glob


class MatplotlibCppConan(ConanFile):
    name = "matplotlib-cpp"
    description = "Extremely simple yet powerful header-only C++ plotting library built on the popular matplotlib."
    topics = ("conan", "matplotlib", "matplotlib-cpp")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lava/matplotlib-cpp"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("matplotlib-cpp-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="matplotlibcpp.h", src=self._source_subfolder, dst="include")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "matplotlib-cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "matplotlib-cpp"
