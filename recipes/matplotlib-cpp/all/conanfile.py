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
        for url_sha in self.conan_data["sources"][self.version]:
            tools.download(url_sha["url"], os.path.basename(url_sha["url"]))
            tools.check_sha256(os.path.basename(url_sha["url"]), url_sha["sha256"])

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses")
        self.copy(pattern="matplotlibcpp.h", dst="include")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "matplotlib-cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "matplotlib-cpp"
