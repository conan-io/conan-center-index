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
        # recent tarballs (since 1096.0.2) are missing mDNSWindows, so for now, Linux only
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux is supported for this package.")
        if tools.Version(self.version) >= "1096.0.2":
            # TCP_NOTSENT_LOWAT is causing build failures for packages built with gcc 4.9
            # the best check would probably be for Linux kernel v3.12, but for now...
            if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
                raise ConanInvalidConfiguration("Only gcc 5 or higher is supported for this package.")
            # __has_c_attribute is not available in Clang 5
            if self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) < "6":
                raise ConanInvalidConfiguration("Only Clang 6 or higher is supported for this package.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _posix_folder(self):
        return os.path.join(self._source_subfolder, "mDNSPosix")

    @property
    def _build_args(self):
        return [
            "os=linux",
            "-j1",
        ]

    @property
    def _build_targets(self):
        return " ".join(["setup", "Daemon", "libdns_sd", "Clients"])

    @property
    def _install_args(self):
        return self._build_args + [
            "INSTBASE={}".format(self.package_folder),
            "STARTUPSCRIPTDIR={}/bin".format(self.package_folder),
            "RUNLEVELSCRIPTSDIR=",
        ]

    @property
    def _install_targets(self):
        # not installing man pages, NSS plugin
        return " ".join(["setup", "InstalledDaemon", "InstalledLib", "InstalledClients"])

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
                autotools.make(args=self._build_args, target=self._build_targets, vars=self._make_env)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Linux":
            for dir in ["bin", "include", "lib", "sbin"]:
                tools.mkdir(os.path.join(self.package_folder, dir))
            with tools.chdir(self._posix_folder):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.make(args=self._install_args, target=self._install_targets, vars=self._make_env)
            # package the daemon in bin too
            tools.rename(os.path.join(self.package_folder, "sbin", "mdnsd"),
                         os.path.join(self.package_folder, "bin", "mdnsd"))
            tools.rmdir(os.path.join(self.package_folder, "sbin"))

    def package_info(self):
        self.cpp_info.libs = ["dns_sd"]

        # add path for daemon (mdnsd) and client (dns-sd)
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
