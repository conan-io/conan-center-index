from conan.tools.files import apply_conandata_patches
from conan import ConanFile, tools$
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.os != "Macos":
            raise ConanInvalidConfiguration(f"{self.name} works only on MacOS")

    def build(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)
        apply_conandata_patches(self)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("create-dmg", dst="bin", src=self._source_subfolder)
        self.copy("*", dst=os.path.join("res", "create-dmg", "support"), src=os.path.join(self._source_subfolder,"support"))

        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        binpath = os.path.join(self.package_folder, "bin")
        self.cpp_info.includedirs = []
        self.output.info(f"Adding to PATH: {binpath}")
        self.env_info.PATH.append(binpath)
