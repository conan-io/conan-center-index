from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class BooleanLiteConan(ConanFile):
    name = "boolean-lite"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/boolean-lite"
    description = "boolean lite - A strong boolean type for C++98 and later in a single-file header-only library"
    topics = ("strong bool", "cpp98/11/17")
    license = "BSL-1.0"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "boolean-lite")
        self.cpp_info.set_property("cmake_target_name", "nonstd::boolean-lite")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "boolean-lite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "boolean-lite"
        self.cpp_info.names["cmake_find_package"] = "nonstd"
        self.cpp_info.names["cmake_find_package_multi"] = "nonstd"
        self.cpp_info.components["booleanlite"].names["cmake_find_package"] = "boolean-lite"
        self.cpp_info.components["booleanlite"].names["cmake_find_package_multi"] = "boolean-lite"
        self.cpp_info.components["booleanlite"].set_property("cmake_target_name", "nonstd::boolean-lite")
        self.cpp_info.components["booleanlite"].bindirs = []
        self.cpp_info.components["booleanlite"].libdirs = []
