import os
from conans import ConanFile, tools

class ResiprocateConan(ConanFile):
    name = "hippomocks"
    description = "Single-header mocking framework."
    topics = ("mock", "hippo", "framework")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dascandy/hippomocks"
    license = "LGPL-2.1 License"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        self.version = "5.0"
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="*", dst=os.path.join("include", "HippoMocks"), src=os.path.join(self._source_subfolder, "HippoMocks"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "HippoMocks"
        self.cpp_info.names["cmake_find_package_multi"] = "HippoMocks"
