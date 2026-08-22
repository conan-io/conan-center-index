from conan import ConanFile
from conan.tools.files import copy, get, download
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class JsmnConan(ConanFile):
    name = "kuliya"
    description = "Algeria's college hierarchy dataset as a C library."
    license = "MIT"
    topics = ("dataset", "api", "dz", "header-only")
    homepage = "https://github.com/dzcode-io/kuliya"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["release"], strip_root=True)
        download(self, **self.conan_data["sources"][self.version]["license"], filename="LICENSE")

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "kuliya.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        copy(self, "data.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
