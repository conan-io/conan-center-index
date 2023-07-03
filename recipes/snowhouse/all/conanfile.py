from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.33.0"


class SnowHouseConan(ConanFile):
    name = "snowhouse"
    description = "An assertion library for C++"
    topics = ("assertion", "header-only")
    package_type = "header-library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/banditcpp/snowhouse"
    license = "BSL-1.0"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE_1_0.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_id(self):
        self.info.clear()
