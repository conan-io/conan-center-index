import os
import re

from conans import ConanFile, tools
from conan.tools.meson import Meson, MesonToolchain
from conans.errors import ConanInvalidConfiguration


required_conan_version = ">=1.33.0"


class SystemdConan(ConanFile):
    name = "systemd"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/systemd/"
    license = "LGPL-2.1-or-later", "GPL-2.0-or-later"
    description = "A suite of basic building blocks for a Linux system"
    topics = ("linux", "udev", "socket", "system", "manager")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_selinux": [True, False],
        "with_lz4": [True, False],
        "with_xz": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_selinux": True,
        "with_lz4": True,
        "with_xz": True,
        "with_zstd": True,
    }
    generators = "pkg_config"
    exports_sources = "patches/**"
    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.name} is only supported for Linux.")

    def build_requirements(self):
        self.build_requires("meson/0.59.2")
        self.build_requires("m4/1.4.19")
        self.build_requires("gperf/3.1")
        self.build_requires("pkgconf/1.7.4")

    def requirements(self):
        self.requires("libcap/2.58")
        self.requires("libmount/2.36.2")
        if self.options.with_selinux:
            self.requires("libselinux/3.2")
        if self.options.with_lz4:
            self.requires("lz4/1.9.3")
        if self.options.with_xz:
            self.requires("xz_utils/5.2.5")
        if self.options.with_zstd:
            self.requires("zstd/1.5.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    @property
    def _so_version(self):
        meson_build = os.path.join(self._source_subfolder, "meson.build")
        with open(meson_build, "r") as build_file:
            for line in build_file:
                match = re.match(r"^libsystemd_version = '(.*)'$", line)
                if match:
                    return match.group(1)
        return ""

    def generate(self):
        yes_no = lambda v: "true" if v else "false"
        fpic = lambda v: "pic" if v else "no-pic"
        toolchain = MesonToolchain(self)
        toolchain.definitions["selinux"] = yes_no(self.options.with_selinux)
        toolchain.definitions["lz4"] = yes_no(self.options.with_lz4)
        toolchain.definitions["xz"] = yes_no(self.options.with_xz)
        toolchain.definitions["zstd"] = yes_no(self.options.with_zstd)
        if self.options.shared:
            toolchain.definitions["static-libsystemd"] = "false"
            toolchain.definitions["static-libudev"] = "false"
        else:
            toolchain.definitions["static-libsystemd"] = fpic(self.options.fPIC)
            toolchain.definitions["static-libudev"] = fpic(self.options.fPIC)
        unrelated = [
            "fdisk", "seccomp", "pwquality", "apparmor", "polkit", "audit",
            "kmod", "microhttpd", "libcryptsetup", "libcurl", "libidn",
            "libidn2", "qrencode", "openssl", "libfido2", "zlib", "xkbcommon",
            "pcre2", "glib", "dbus", "blkid", "gcrypt", "p11kit", "ima",
            "smack", "bzip2", "gnutls", "idn", "initrd", "binfmt", "vconsole",
            "quotacheck", "tmpfiles", "environment-d", "sysusers", "firstboot",
            "randomseed", "backlight", "rfkill", "xdg-autostart", "logind",
            "hibernate", "machined", "portabled", "userdb", "hostnamed",
            "timedated", "timesyncd", "localed", "networkd", "resolve",
            "coredump", "pstore", "efi", "nss-myhostname", "nss-mymachines",
            "nss-resolve", "nss-systemd", "hwdb", "tpm", "man", "html", "utmp",
            "ldconfig", "adm-group", "wheel-group", "gshadow", "install-tests",
            "link-udev-shared", "link-systemctl-shared", "analyze", "pam",
            "link-networkd-shared", "link-timesyncd-shared", "kernel-install",
            "libiptc", "elfutils", "repart", "homed", "importd", "acl",
            "dns-over-tls", "gnu-efi", "valgrind", "log-trace", "tests",
            "slow-tests", "fuzz-tests"]
        for opt in unrelated:
            toolchain.definitions[opt] = "false"
        toolchain.definitions["rootprefix"] = self.package_folder
        toolchain.definitions["pkgconfigdatadir"] = self.build_folder
        toolchain.generate()

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        meson_build = os.path.join(self._source_subfolder, "meson.build")
        tools.replace_in_file(
            meson_build, """relative_source_path = run_command('realpath',
                                   '--relative-to=@0@'.format(project_build_root),
                                   project_source_root).stdout().strip()""",
            f"relative_source_path = '../{self._source_subfolder}'")
        tools.replace_in_file(meson_build, "if not cc.has_header('sys/capability.h')",
                                           "libcap = dependency('libcap')\nif not cc.has_header('sys/capability.h', dependencies:libcap)")
        tools.replace_in_file(meson_build, "have = libselinux.found()",
                                           "cc.has_header('selinux/selinux.h',dependencies:libselinux)\n    have = libselinux.found()")
        tools.replace_in_file(meson_build, "link_whole : libudev_basic,\n        dependencies : [threads]",
                              "link_whole : libudev_basic,\n        dependencies : [threads, libselinux]")

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        self._meson.configure(source_folder=self._source_subfolder)
        return self._meson

    def build(self):
        self._patch_sources()
        meson = self._configure_meson()
        meson.build("systemd_static")

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()

        #self.copy("*.h", os.path.join("include", "systemd"), os.path.join(self._source_subfolder, "src", "systemd"))
        #
        #if self.options.shared:
        #    self.copy("libsystemd.so*", "lib", self._build_subfolder)
        #    self.copy("liudev.so.*", "lib", self._build_subfolder)
        #else:
        #    self.copy("libsystemd.a", "lib", self._build_subfolder)
        #    self.copy("libudev.a", "lib", self._build_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["systemd", "udev"]
        self.cpp_info.version = tools.Version(self.version).major
        self.cpp_info.system_libs = ["rt", "pthread", "dl"]
        # TODO: Create component for libudev
