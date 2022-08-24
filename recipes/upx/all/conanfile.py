from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class UPXConan(ConanFile):
    name = "upx"
    description = "UPX - the Ultimate Packer for eXecutables "
    license = "GPL-2.0-or-later", "special-exception-for-compressed-executables"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://upx.github.io/"
    topics = ("packer", "executable", "compression", "size", "reduction", "small", "footprintt")
    no_copy_source = True
    settings = "os", "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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
        tools.get(**self._conan_data_sources(),
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        if self.settings.os == "Windows":
            self.copy("upx.exe", src=self._source_subfolder, dst="bin")
        else:
            self.copy("upx", src=self._source_subfolder, dst="bin")

    def package_info(self):
        self.cpp_info.libdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)

        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        upx = os.path.join(bin_path, f"upx{bin_ext}")
        self.user_info.upx = upx
