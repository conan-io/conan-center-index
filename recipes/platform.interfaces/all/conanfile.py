import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class PlatformInterfacesConan(ConanFile):
    name = "platform.interfaces"
    license = "The Unlicense"
    homepage = "https://github.com/linksplatform/Interfaces"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Contains common interfaces that did not fit in any major category."
    topics = ("platform", "concepts", "header-only")
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _source_subfolder(self):
        return self.name

    @property
    def _subfolder_sources(self):
        return os.path.join(self._source_subfolder, "cpp", "Platform.Interfaces")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "Visual Studio": "16",
            "clang": "11",
            "apple-clang": "11"
        }

    def validate(self):
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"platform.interfaces/{self.version} "
                                            f"requires C++20 with {self.settings.compiler}, "
                                            f"which is not supported "
                                            f"by {self.settings.compiler} {self.settings.compiler.version} ")
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 20)

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

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "platform.interfaces"
        self.cpp_info.names["cmake_find_package_multi"] = "platform.interfaces"
