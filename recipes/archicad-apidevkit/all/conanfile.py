from conan import ConanFile
from conan.tools.files import get
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.00"


class ArchicadApidevkitConan (ConanFile):
    name = "archicad-apidevkit"
    description = "The General API Development Kit enables software developers to extend the functionality of Archicad"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://archicadapi.graphisoft.com/"
    license = "https://archicadapi.graphisoft.com/documentation/license-agreement"
    settings = "os", "arch"
    no_copy_source = True
    topics = "API, Archicad, development"

    @property
    def _source_subfolder(self):
        return self.source_folder

    @property
    def _acdevkit_arch(self):
        return str(self.settings.arch)

    def validate(self):
        if (not (self.version in self.conan_data["sources"]) or
                not (str(self.settings.os) in self.conan_data["sources"][self.version])):
            raise ConanInvalidConfiguration(
                "Binaries for this combination of architecture/version/os not available")

    def build(self):
        get(self, **self.conan_data["sources"][self.version][str(self.settings.os)][self._acdevkit_arch], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*", symlinks=True)
