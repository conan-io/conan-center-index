from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class Pybind11JsonConan(ConanFile):
    name = "pybind11_json"
    homepage = "https://github.com/pybind/pybind11_json"
    description = "An nlohmann_json to pybind11 bridge"
    topics = (
        "conan",
        "header-only",
        "json",
        "nlohmann_json",
        "pybind11",
        "pybind11_json",
        "python",
        "python-binding",
    )
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    license = "BSD-3-Clause"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def requirements(self):
        self.requires("nlohmann_json/3.9.1")
        self.requires("pybind11/2.6.2")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="LICENSE*", src=self._source_subfolder, dst="licenses")
        self.copy(
            "*", dst="include", src=os.path.join(self._source_subfolder, "include")
        )

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "pybind11_json"
        self.cpp_info.names["cmake_find_package_multi"] = "pybind11_json"
