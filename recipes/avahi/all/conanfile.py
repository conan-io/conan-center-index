from conan import ConanFile, tools
from conans import AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class AvahiConan(ConanFile):
    name = "avahi"
    # --enable-compat-libdns_sd means that this recipe provides the mdnsresponder compile interface
    provides = "mdnsresponder"
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
        if self.settings.os != "Linux" or tools.build.cross_building(self, self):
            raise ConanInvalidConfiguration("Only Linux is supported for this package.")

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _configure_args(self):
        yes_no = lambda v: "yes" if v else "no"
        return [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--disable-gtk3",
            "--disable-mono",
            "--disable-python",
            "--disable-qt5",
            "--disable-monodoc",
            "--enable-compat-libdns_sd",
            "--with-systemdsystemunitdir={}/lib/systemd/system".format(self.package_folder),
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
        tools.files.rmdir(self, os.path.join(self.package_folder, "etc"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Avahi"
        self.cpp_info.names["cmake_find_package_multi"] = "Avahi"

        for lib in ("client", "common", "core", "glib", "gobject", "libevent", "compat-libdns_sd"):
            avahi_lib = "avahi-{}".format(lib)
            self.cpp_info.components[lib].names["cmake_find_package"] = lib
            self.cpp_info.components[lib].names["cmake_find_package_multi"] = lib
            self.cpp_info.components[lib].names["pkg_config"] = avahi_lib
            self.cpp_info.components[lib].libs = [avahi_lib]
            self.cpp_info.components[lib].includedirs = [os.path.join("include", avahi_lib)]
        self.cpp_info.components["compat-libdns_sd"].libs = ["dns_sd"]

        self.cpp_info.components["client"].requires = ["common", "dbus::dbus"]
        self.cpp_info.components["common"].system_libs = ["pthread"]
        self.cpp_info.components["core"].requires = ["common"]
        self.cpp_info.components["glib"].requires = ["common", "glib::glib"]
        self.cpp_info.components["gobject"].requires = ["client", "glib"]
        self.cpp_info.components["libevent"].requires = ["common", "libevent::libevent"]
        self.cpp_info.components["compat-libdns_sd"].requires = ["client"]

        for app in ("autoipd", "browse", "daemon", "dnsconfd", "publish", "resolve", "set-host-name"):
            avahi_app = "avahi-{}".format(app)
            self.cpp_info.components[app].names["cmake_find_package"] = app
            self.cpp_info.components[app].names["cmake_find_package_multi"] = app
            self.cpp_info.components[app].names["pkg_config"] = avahi_app

        self.cpp_info.components["autoipd"].requires = ["libdaemon::libdaemon"]
        self.cpp_info.components["browse"].requires = ["client", "gdbm::gdbm"]
        self.cpp_info.components["daemon"].requires = ["core", "expat::expat", "libdaemon::libdaemon"]
        self.cpp_info.components["dnsconfd"].requires = ["common", "libdaemon::libdaemon"]
        self.cpp_info.components["publish"].requires = ["client"]
        self.cpp_info.components["resolve"].requires = ["client"]
        self.cpp_info.components["set-host-name"].requires = ["client"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
