import os
from conans import ConanFile, tools

required_conan_version = ">=1.28.0"

class InjaConan(ConanFile):
    name = "inja"
    license = "MIT"
    homepage = "https://github.com/pantor/inja"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Inja is a template engine for modern C++, loosely inspired by jinja for python"
    topics = ("conan", "jinja2", "string templates", "templates engine")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("nlohmann_json/3.9.1")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "inja"
        self.cpp_info.filenames["cmake_find_package_multi"] = "inja"
        self.cpp_info.names["cmake_find_package"] = "pantor"
        self.cpp_info.names["cmake_find_package_multi"] = "pantor"
        self.cpp_info.components["libinja"].names["cmake_find_package"] = "inja"
        self.cpp_info.components["libinja"].names["cmake_find_package_multi"] = "inja"
        self.cpp_info.components["libinja"].requires = ["nlohmann_json::nlohmann_json"]
