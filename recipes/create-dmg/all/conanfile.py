from conan import ConanFile
from conan.tools.files import apply_conandata_patches, get, copy, rmdir
from conan.tools.layout import basic_layout
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
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = 'patches/**'

    def layout(self):
        basic_layout(self)

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
        del self.settings.compiler
        del self.settings.build_type

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        binpath = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(binpath)
