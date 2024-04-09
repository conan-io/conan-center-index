import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, rm
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.53.0"


class AvahiConan(ConanFile):
    name = "avahi"
    # --enable-compat-libdns_sd means that this recipe provides the mdnsresponder compile interface
    provides = "mdnsresponder"
    description = "Avahi - Service Discovery for Linux using mDNS/DNS-SD -- compatible with Bonjour"
    topics = ("bonjour", "dns", "dns-sd", "mdns")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lathiat/avahi"
    license = "LGPL-2.1-only"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/2.78.1")
        self.requires("expat/2.5.0")
        self.requires("libdaemon/0.14")
        self.requires("dbus/1.15.8")
        self.requires("gdbm/1.23")
        self.requires("libevent/2.1.12")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux.")

    def build_requirements(self):
        self.tool_requires("glib/<host_version>")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        if can_run(self):
            VirtualRunEnv(self).generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--enable-compat-libdns_sd")
        tc.configure_args.append("--enable-introspection=no")
        tc.configure_args.append("--disable-gtk3")
        tc.configure_args.append("--disable-mono")
        tc.configure_args.append("--disable-monodoc")
        tc.configure_args.append("--disable-python")
        tc.configure_args.append("--disable-qt5")
        tc.configure_args.append("--with-systemdsystemunitdir=/lib/systemd/system")
        tc.configure_args.append("--with-distro=none")
        tc.configure_args.append("ac_cv_func_strlcpy=no")
        tc.configure_args.append("ac_cv_func_setproctitle=no")
        tc.generate()
        AutotoolsDeps(self).generate()
        PkgConfigDeps(self).generate()
        # Override Avahi's problematic check for the pkg-config executable.
        env = Environment()
        env.define("have_pkg_config", "yes")
        env.vars(self).save_script("conanbuild_pkg_config")

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "run"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        for lib in ("client", "common", "core", "glib", "gobject", "libevent", "compat-libdns_sd"):
            avahi_lib = f"avahi-{lib}"
            self.cpp_info.components[lib].set_property("pkg_config_name", avahi_lib)
            self.cpp_info.components[lib].names["cmake_find_package"] = lib
            self.cpp_info.components[lib].names["cmake_find_package_multi"] = lib
            self.cpp_info.components[lib].libs = [avahi_lib]
            self.cpp_info.components[lib].includedirs = ["include", os.path.join("include", avahi_lib)]
        self.cpp_info.components["compat-libdns_sd"].libs = ["dns_sd"]

        self.cpp_info.components["client"].requires = ["common", "dbus::dbus"]
        self.cpp_info.components["common"].system_libs = ["pthread"]
        self.cpp_info.components["core"].requires = ["common"]
        self.cpp_info.components["glib"].requires = ["common", "glib::glib"]
        self.cpp_info.components["gobject"].requires = ["client", "glib"]
        self.cpp_info.components["libevent"].requires = ["common", "libevent::libevent"]
        self.cpp_info.components["compat-libdns_sd"].requires = ["client"]

        for app in ("autoipd", "browse", "daemon", "dnsconfd", "publish", "resolve", "set-host-name"):
            avahi_app = f"avahi-{app}"
            self.cpp_info.components[app].set_property("pkg_config_name", avahi_app)
            self.cpp_info.components[app].names["cmake_find_package"] = app
            self.cpp_info.components[app].names["cmake_find_package_multi"] = app

        self.cpp_info.components["autoipd"].requires = ["libdaemon::libdaemon"]
        self.cpp_info.components["browse"].requires = ["client", "gdbm::gdbm"]
        self.cpp_info.components["daemon"].requires = ["core", "expat::expat", "libdaemon::libdaemon"]
        self.cpp_info.components["dnsconfd"].requires = ["common", "libdaemon::libdaemon"]
        self.cpp_info.components["publish"].requires = ["client"]
        self.cpp_info.components["resolve"].requires = ["client"]
        self.cpp_info.components["set-host-name"].requires = ["client"]

        # TODO: Remove after dropping Conan 1.x support
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
