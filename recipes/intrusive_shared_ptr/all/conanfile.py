from pathlib import Path

from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd

required_conan_version = ">=2.1"

class IsptrRecipe(ConanFile):

    name = "intrusive_shared_ptr"
    description = "Intrusive reference counting smart pointer, highly configurable reference counted base class and various adapters."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gershnik/intrusive_shared_ptr"
    topics = ("smart-pointer", "intrusive", "header-only", "header-library")

    package_type = "header-library"
    no_copy_source = True

    def validate(self):
        check_min_cppstd(self, 17)

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="*.h", keep_path=True,
             src=Path(self.source_folder) / "inc",
             dst=Path(self.package_folder) / "include")
        copy(self, pattern="LICENSE.txt", src=self.source_folder, dst=Path(self.package_folder) / "licenses")

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "isptr")
        self.cpp_info.set_property("cmake_target_name", "isptr::isptr")
        self.cpp_info.set_property("pkg_config_name",  "isptr")
