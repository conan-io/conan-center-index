from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class AvahiConan(ConanFile):
    name = "avahi"
    description = "Avahi - Service Discovery for Linux using mDNS/DNS-SD -- compatible with Bonjour"
    topics = ("avahi", "Bonjour", "DNS-SD", "mDNS")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lathiat/avahi"
    license = "LGPL-2.1-only"
    settings = "os", "arch", "compiler", "build_type"
    generators = "pkg_config"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("glib/2.68.3")
        self.requires("expat/2.4.1")
        self.requires("libdaemon/0.14")
        self.requires("dbus/1.12.20")
        self.requires("gdbm/1.19")
        self.requires("libevent/2.1.12")

    def validate(self):
        if self.settings.os != "Linux" or tools.cross_building(self):
            raise ConanInvalidConfiguration("Only Linux is supported for this package.")

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _configure_args(self):
        return [
            "--disable-gtk3",
            "--disable-mono",
            "--disable-python",
            "--disable-qt5",
            "--disable-monodoc",
            "--enable-compat-libdns_sd",
        ]

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(configure_dir=self._source_subfolder, args=self._configure_args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        autotools = self._configure_autotools()
        autotools.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = [
            "avahi-client",
            "avahi-common",
            "avahi-core",
            "avahi-glib",
            "avahi-gobject",
            "avahi-libevent",
            "dns_sd"
        ]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
