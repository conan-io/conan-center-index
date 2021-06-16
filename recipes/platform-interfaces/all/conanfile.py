from conans import ConanFile, CMake, tools
import os


class PlatformInterfacesConan(ConanFile):
    name = "platform.interfaces"
    license = "The Unlicense"
    homepage = "https://github.com/linksplatform/Interfaces"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Contains common interfaces that did not fit in any major category."
    topics = ("platform", "concepts", "header.only")
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _self_name(self):
        return "interfaces"

    @property
    def _source_subfolder(self):
        return "Interfaces"

    @property
    def _subfolder_sources(self):
        return os.path.join(self._source_subfolder, "cpp", f"Platform.{self._self_name}")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

        url: str = self.conan_data["sources"][self.version]["url"]
        version_pos: int = url.find(f"_{self.version}")
        csharp_version: str = url[(version_pos - 5):version_pos]

        extracted_folder = f"Interfaces-{csharp_version}_{self.version}"
        os.rename(extracted_folder, self._source_subfolder)

    def package(self):
        self.copy("*.h", dst="include", src=self._subfolder_sources)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
