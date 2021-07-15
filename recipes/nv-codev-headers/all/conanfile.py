from enum import auto
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.35.0"

class FFNvEncHeaders(ConanFile):
    name = "nv-codec-headers"
    description = "FFmpeg version of headers required to interface with Nvidia's codec APIs"
    topics = ("ffmpeg", "video", "nvidia", "headers")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/FFmpeg/nv-codec-headers"
    license = "MIT"

    _autotools = None

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        autotools = self._configure_autotools()
        vars = autotools.vars
        autotools.install(args=["PREFIX={}".format(self.package_folder)])
