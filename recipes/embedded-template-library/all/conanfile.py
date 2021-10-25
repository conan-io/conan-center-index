import os

from conans import ConanFile, tools


class EmbeddedTemplateLibraryConan(ConanFile):
    name = "embedded-template-library"
    license = "MIT"
    homepage = "https://www.etlcpp.com/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A C++ template library for embedded applications"
    topics = ("C++", "embedded", "template", "container", "utility", "framework", "messaging")
    no_copy_source = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        self.copy("LICENSE", "licenses")
        self.copy(os.path.join("include", "etl", "*.h"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "etl"
        self.cpp_info.names["cmake_find_package_multi"] = "etl"
