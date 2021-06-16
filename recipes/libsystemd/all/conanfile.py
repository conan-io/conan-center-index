import os
import re

from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class LibsystemdConan(ConanFile):
    name = "libsystemd"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/systemd/"
    description = "System and Service Manager API library"
    topics = ("conan", "systemd", "libsystemd")
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux supported")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if tools.Version(self.version) >= "248.3":
            self.build_requires("meson/0.58.1")
        else:
            # incompatible change in meson/0.57.2:
            # https://github.com/mesonbuild/meson/pull/8526
            self.build_requires("meson/0.57.1")
        self.build_requires("m4/1.4.18")
        self.build_requires("gperf/3.1")
        self.build_requires("pkgconf/1.7.4")

    def requirements(self):
        self.requires("libcap/2.50")
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

    def _configure_meson(self):
        meson = Meson(self)
        defs = dict()
        defs["selinux"] = "true" if self.options.with_selinux else "false"
        defs["lz4"] = "true" if self.options.with_lz4 else "false"
        defs["xz"] = "true" if self.options.with_xz else "false"
        defs["zstd"] = "true" if self.options.with_zstd else "false"

        if self.options.shared:
            defs["static-libsystemd"] = "false"
        elif self.options.fPIC:
            defs["static-libsystemd"] = "pic"
        else:
            defs["static-libsystemd"] = "no-pic"

        # options unrelated to libsystemd
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
            "dns-over-tls", "gnu-efi", "valgrind", "log-trace"]
        for opt in unrelated:
            defs[opt] = "false"

        # 'rootprefix' is unused during libsystemd packaging but systemd v248
        # build files require 'prefix' to be a subdirectory of 'rootprefix'.
        defs["rootprefix"] = self.package_folder

        meson.configure(source_folder=self._source_subfolder,
                        build_folder=self._build_subfolder, defs=defs)
        return meson

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        meson_build = os.path.join(self._source_subfolder, "meson.build")
        tools.replace_in_file(
            meson_build, """relative_source_path = run_command('realpath',
                                   '--relative-to=@0@'.format(project_build_root),
                                   project_source_root).stdout().strip()""",
            "relative_source_path = '../{}'".format(self._source_subfolder))

    def build(self):
        self._patch_sources()

        meson = self._configure_meson()
        target = ("libsystemd.so.{}".format(self._so_version)
                  if self.options.shared else "libsystemd.a")
        meson.build(targets=["version.h", target])

    def package(self):
        self.copy(pattern="LICENSE.LGPL2.1", dst="licenses",
                  src=self._source_subfolder)
        self.copy(pattern="*.h", dst=os.path.join("include", "systemd"),
                  src=os.path.join(self._source_subfolder, "src", "systemd"))

        if self.options.shared:
            self.copy(pattern="libsystemd.so", dst="lib",
                      src=self._build_subfolder, symlinks=True)
            self.copy(pattern="libsystemd.so.{}".format(self._so_version.split('.')),
                      dst="lib", src=self._build_subfolder, symlinks=True)
            self.copy(pattern="libsystemd.so.{}".format(self._so_version),
                      dst="lib", src=self._build_subfolder, symlinks=True)
        else:
            self.copy(pattern="libsystemd.a", dst="lib",
                      src=self._build_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["systemd"]
        # FIXME: this `.version` should only happen for the `pkg_config`
        #  generator (see https://github.com/conan-io/conan/issues/8202)
        # systemd uses only major version in its .pc file
        self.cpp_info.version = tools.Version(self.version).major
        self.cpp_info.system_libs = ["rt", "pthread", "dl"]
