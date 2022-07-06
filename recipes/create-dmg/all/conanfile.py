from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def validate(self):
        if self.settings.os != "Macos":
            raise ConanInvalidConfiguration(f"{self.name} works only on MacOS")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("create-dmg", dst="bin", src=self._source_subfolder)
        self.copy("*", dst=os.path.join("res", "create-dmg", "support"), src=os.path.join(self._source_subfolder,"support"))

        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        binpath = os.path.join(self.package_folder, "bin")
        self.cpp_info.includedirs = []
        self.output.info(f"Adding to PATH: {binpath}")
        self.env_info.PATH.append(binpath)
