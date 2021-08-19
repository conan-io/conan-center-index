from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class MdnsResponderConan(ConanFile):
    name = "mdnsresponder"
    description = "Conan package for Apple's mDNSResponder"
    topics = ("Bonjour", "DNS-SD", "mDNS")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://opensource.apple.com/tarballs/mDNSResponder/"
    license = "Apache-2.0", "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["patches/**"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.os not in ["Linux", "Windows"]:
            raise ConanInvalidConfiguration("Only Linux and Windows are supported for this package.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _make(self):
        make = tools.get_env("CONAN_MAKE_PROGRAM", tools.which("make"))
        if not make:
            raise ConanInvalidConfiguration("This package needs 'make' in the path to build")
        return "{} CFLAGS=-std=gnu99".format(make)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.os == "Linux":
            with tools.chdir(os.path.join(self._source_subfolder, "mDNSPosix")):
                self.run("{} os=linux".format(self._make))

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Linux":
            with tools.chdir(os.path.join(self._source_subfolder, "mDNSPosix")):
                self.run("{} install os=linux".format(self._make))

    def package_info(self):
        pass
