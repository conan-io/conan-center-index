from conan import ConanFile
from conan.tools.files import get, copy
import os

required_conan_version = ">=1.52.0"


class ArteryFontFormatConan(ConanFile):
    name = "artery-font-format"
    license = "MIT"
    homepage = "https://github.com/Chlumsky/artery-font-format"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Artery Atlas Font format library"
    topics = ("artery", "font", "atlas")
    package_type = "header-library"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        # header only: no build step
        pass

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=self.source_folder,
        )
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=self.source_folder,
        )
