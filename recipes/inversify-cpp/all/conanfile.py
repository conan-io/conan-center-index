from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class InversifyCppConan(ConanFile):
    name = "inversify-cpp"
    description = "C++17 inversion of control and dependency injection container library"
    topics = ("conan", "inversify-cpp", "ioc", "container", "dependency", "injection")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mosure/inversify-cpp"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
       tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.includedirs = ['include']
