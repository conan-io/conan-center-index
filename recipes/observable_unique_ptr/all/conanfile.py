import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.build import check_min_cppstd

required_conan_version = ">=2.1"


class OupConan(ConanFile):
    name = "observable_unique_ptr"
    description = "Unique-ownership smart pointers with observable lifetime."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cschreib/observable_unique_ptr"
    topics = ("memory", "smart-pointer")
    package_type = "header-library"
    settings = "compiler"

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
    
    def package_id(self):
        self.info.clear()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "oup")
        self.cpp_info.set_property("cmake_target_name", "oup::oup")
        self.cpp_info.set_property("pkg_config_name",  "oup")
