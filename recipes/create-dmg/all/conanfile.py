from conan import ConanFile
from conan.tools.files import apply_conandata_patches, get, copy, rmdir
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class CreateDmgConan(ConanFile):
    name = "create-dmg"
    description = "A shell script to build fancy DMGs"
    license = "MIT"
    topics = "command-line", "dmg"
    homepage = "https://github.com/create-dmg/create-dmg"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os"
    exports_sources = 'patches/**'

    def layout(self):
        pass

    def validate(self):
        if self.settings.os != "Macos":
            raise ConanInvalidConfiguration(f"{self.name} works only on MacOS")

    def source(self):
        pass

    def build(self):
        get(self, **self.conan_data["sources"][self.version],
                strip_root=True, destination=self.source_folder)
        apply_conandata_patches(self)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="create-dmg", dst=os.path.join(self.package_folder, "bin"), src=self.source_folder)
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "res", "create-dmg", "support"), src=os.path.join(self.source_folder,"support"))

        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        binpath = os.path.join(self.package_folder, "bin")
        self.cpp_info.includedirs = []
        self.output.info(f"Adding to PATH: {binpath}")
        self.env_info.PATH.append(binpath)
