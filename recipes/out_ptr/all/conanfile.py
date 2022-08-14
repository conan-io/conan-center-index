from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.46.0"


class OutPtrConan(ConanFile):
    name = "out_ptr"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/soasis/out_ptr"
    description = "a C++11 implementation of std::out_ptr (p1132), as a standalone library"
    topics = ("utility", "backport")
    settings = "os", "arch", "build_type", "compiler"
    no_copy_source = True

    def package_id(self):
        self.info.header_only()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"),
                            dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
