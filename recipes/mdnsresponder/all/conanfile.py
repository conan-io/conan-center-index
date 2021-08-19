from conans import ConanFile, tools, AutoToolsBuildEnvironment
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
    def _posix_folder(self):
        return os.path.join(self._source_subfolder, "mDNSPosix")

    @property
    def _make_args(self):
        return [
            "os=linux",
        ]

    @property
    def _make_env(self):
        return {
            "CFLAGS": "-std=gnu99",
        }

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.os == "Linux":
            with tools.chdir(self._posix_folder):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.make(args=self._make_args, vars=self._make_env)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Linux":
            with tools.chdir(self._posix_folder):
                autotools = AutoToolsBuildEnvironment(self)
                args = self._make_args
                args.append("INSTBASE={}".format(self.package_folder))
                autotools.install(args=args, vars=self._make_env)

    def package_info(self):
        pass
