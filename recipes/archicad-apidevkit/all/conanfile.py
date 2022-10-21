from conans import tools
from conan import ConanFile
from conan.tools.files import copy, get
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.46.0"


class ArchicadApidevkitConan (ConanFile):
    name = "archicad-apidevkit"
    description = "The General API Development Kit enables software developers to extend the functionality of Archicad"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://archicadapi.graphisoft.com/"
    license = "LicenseRef-LICENSE"
    settings = "os", "arch", "build_type", "compiler"
    no_copy_source = True
    topics = "api", "archicad", "development"
    short_paths = True

    @property
    def _acdevkit_arch(self):
        return str(self.settings.arch)

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

    def validate(self):
        if not self.info.settings.os in ("Macos", "Windows"):
            raise ConanInvalidConfiguration(
                f"{self.ref} is not supported by the OS {self.info.settings.os}")
        if not str(self.settings.arch) in ("x86_64"):
            raise ConanInvalidConfiguration(
                f"{self.ref} is not supported yet.")

    def build(self):
        get(self, **self.conan_data["sources"][self.version][str(self.settings.os)]
                  [self._acdevkit_arch][0], destination=self.build_folder, strip_root=True)
        tools.download(filename="LICENSE", **self.conan_data["sources"][self.version][str(
            self.settings.os)][self._acdevkit_arch][1])

    def package(self):
        copy(self, "*", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"))
        copy(self, "LICENSE", src=self.build_folder, dst=os.path.join(self.package_folder, "licenses"))
        os.remove(os.path.join(self.package_folder, "bin/LICENSE"))
