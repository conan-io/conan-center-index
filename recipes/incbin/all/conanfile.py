from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.50.0"


class IncbinConan(ConanFile):
    name = "incbin"
    description = "Include binary files in C/C++"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/graphitemaster/incbin/"
    topics = ("include", "binary", "preprocess", "header-only")
    package_type = "header-library"
    settings = "compiler"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("Currently incbin recipe is not supported for Visual Studio because it requires external command 'incbin'.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "UNLICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "incbin.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)

    def package_id(self):
        self.info.clear()
