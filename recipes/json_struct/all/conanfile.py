from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"

class JsonStructConan(ConanFile):
    name = "json_struct"
    description = "json_struct is a single header only C++ library for parsing JSON directly to C++ structs and vice versa"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jorgen/json_struct"

    topics = ("serialization", "deserialization", "reflection", "json")

    settings = "os", "compiler", "build_type", "arch"
    package_type = "header-library"
    no_copy_source = True

    def validate(self):
        check_min_cppstd(self, 14)

    def layout(self):
        basic_layout(self, src_folder="src")
    
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
    
    def package_id(self):
        self.info.clear()

    # Copy all files to the package folder
    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(
            self,
            "*.h",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"),
        )
