from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LinuxHeadersGenericConan(ConanFile):
    name = "linux-headers-generic"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.kernel.org/"
    license = "GPL-2.0-only"
    description = "Generic Linux kernel headers"
    topics = ("linux", "headers", "generic")
    settings = "os", "arch", "build_type", "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        del self.info.settings.os
        del self.info.settings.build_type
        del self.info.settings.compiler

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("linux-headers-generic supports only Linux")
        if hasattr(self, "settings_build") and tools.cross_building(self):
            raise ConanInvalidConfiguration("linux-headers-generic can not be cross-compiled")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        with tools.chdir(os.path.join(self._source_subfolder)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make(target="headers")

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("include/*.h", src=os.path.join(self._source_subfolder, "usr"))
