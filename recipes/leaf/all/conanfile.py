from conans import tools, ConanFile
import os

required_conan_version = ">=1.33.0"


class BoostLeafConan(ConanFile):
    name = "leaf"
    description = "Lightweight Error Augmentation Framework"
    topics = ("conan", "leaf", "boost", "error")
    license = "BSL-1.0"
    homepage = "https://github.com/boostorg/leaf"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="LICENSE_1_0.txt", src=self._source_subfolder, dst="licenses")
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "leaf"
        self.cpp_info.filenames["cmake_find_package_multi"] = "leaf"
        self.cpp_info.names["cmake_find_package"] = "Boost"
        self.cpp_info.names["cmake_find_package_multi"] = "Boost"
        self.cpp_info.components["leaflib"].names["cmake_find_package"] = "leaf"
        self.cpp_info.components["leaflib"].names["cmake_find_package_multi"] = "leaf"
