from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class RapidjsonConan(ConanFile):
    name = "rapidjson"
    description = "A fast JSON parser/generator for C++ with both SAX/DOM style API"
    topics = ("rapidjson", "json", "parser", "generator")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://rapidjson.org"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self)

    def source(self):
       get(self, **self.conan_data["sources"][self.version], strip_root=True,
                    destination=self.source_folder)

    def package(self):
        copy(self, pattern="license.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "RapidJSON")
        self.cpp_info.set_property("cmake_target_name", "rapidjson")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "RapidJSON"
        self.cpp_info.names["cmake_find_package_multi"] = "RapidJSON"
