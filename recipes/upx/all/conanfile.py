import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get

required_conan_version = ">=1.47.0"


class UPXConan(ConanFile):
    name = "upx"
    description = "UPX - the Ultimate Packer for eXecutables "
    license = ("GPL-2.0-or-later", "special-exception-for-compressed-executables")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://upx.github.io/"
    topics = ("packer", "executable", "compression", "size", "reduction", "small", "footprintt", "pre-built")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def _conan_data_sources(self):
        # Don't surround this with try/catch to catch unknown versions
        conandata_version = self.conan_data["sources"][self.version]
        try:
            return conandata_version[str(self.settings.os)][str(self.settings.arch)]
        except KeyError:
            return None

    def validate(self):
        if not self._conan_data_sources():
            raise ConanInvalidConfiguration(f"This recipe has no upx binary for os/arch={self.settings.os}/{self.settings.arch}")

    def build(self):
        get(self, **self._conan_data_sources(), strip_root=True)

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYING",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        extension = ".exe" if self.settings.os == "Windows" else ""
        copy(self, f"upx{extension}",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        upx = os.path.join(bin_path, f"upx{bin_ext}")
        self.conf_info.define("user.upx:upx", upx)

        # TODO: to remove in conan v2
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
        self.user_info.upx = upx
