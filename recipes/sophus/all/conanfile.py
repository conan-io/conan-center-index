from conans import ConanFile, tools
import os


class SophusConan(ConanFile):
    name = "sophus"
    description = "C++ implementation of Lie Groups using Eigen."
    topics = ("conan", "eigen", "numerical", "math")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://strasdat.github.io/Sophus/"
    license = "MIT"
    no_copy_source = True

    requires = "eigen/3.3.7"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name.capitalize() + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", src=os.path.join(self._source_subfolder, "sophus"), dst=os.path.join("include", "sophus"), keep_path=False)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Sophus"
        self.cpp_info.names["cmake_find_package_multi"] = "Sophus"
