from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"


class CreateDmgConan(ConanFile):
    name = "create-dmg"
    description = "A shell script to build fancy DMGs"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/create-dmg/create-dmg"
    topics = ("command-line", "dmg")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.os != "Macos":
            raise ConanInvalidConfiguration(f"{self.name} works only on MacOS")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="create-dmg", dst=os.path.join(self.package_folder, "bin"), src=self.source_folder)
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "res"), src=os.path.join(self.source_folder, "support"))

        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res"]

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
