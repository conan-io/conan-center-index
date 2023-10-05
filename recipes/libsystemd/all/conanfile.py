import os
import re
import tarfile

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, replace_in_file, download, move_folder_contents
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version

required_conan_version = ">=1.60.0"


class LibsystemdConan(ConanFile):
    name = "libsystemd"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/systemd/"
    description = "System and Service Manager API library"
    topics = ("systemd", "service", "manager")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    provides = "libudev"
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

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libcap/2.69")
        self.requires("libmount/2.39.2")
        if Version(self.version) >= "251.18":
            self.requires("libxcrypt/4.4.36")
        if self.options.with_selinux:
            self.requires("libselinux/3.5")
        if self.options.with_lz4:
            self.requires("lz4/1.9.4")
        if self.options.with_xz:
            self.requires("xz_utils/5.4.5")
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux supported")

    def build_requirements(self):
        self.tool_requires("meson/1.3.0")
        self.tool_requires("m4/1.4.19")
        self.tool_requires("gperf/3.1")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        # Extract using standard Python tools due to Conan's unzip() not handling backslashes in
        # 'units/system-systemd\x2dcryptsetup.slice', etc. correctly.
        download(self, **self.conan_data["sources"][self.version], filename="sources.tar.gz")
        with tarfile.open("sources.tar.gz", "r:gz") as tar:
            tar.extractall()
        move_folder_contents(self, os.path.join(self.source_folder, f"systemd-stable-{self.version}"), self.source_folder)

    @property
    def _so_version(self):
        meson_build = os.path.join(self.source_folder, "meson.build")
        with open(meson_build, "r", encoding="utf-8") as build_file:
            for line in build_file:
                match = re.match(r"^libsystemd_version = '(.*)'$", line)
                if match:
                    return match.group(1)
        return ""

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = MesonToolchain(self)
        tc.project_options["werror"] = False
        tc.project_options["selinux"] = ("true" if self.options.with_selinux
                                         else "false")
        tc.project_options["lz4"] = ("true" if self.options.with_lz4
                                     else "false")
        tc.project_options["xz"] = "true" if self.options.with_xz else "false"
        tc.project_options["zstd"] = ("true" if self.options.with_zstd
                                      else "false")

        if self.options.shared:
            tc.project_options["static-libsystemd"] = "false"
            tc.project_options["static-libudev"] = "false"
        elif self.options.fPIC:
            tc.project_options["static-libsystemd"] = "pic"
            tc.project_options["static-libudev"] = "pic"
        else:
            tc.project_options["static-libsystemd"] = "no-pic"
            tc.project_options["static-libudev"] = "no-pic"

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
            "dns-over-tls", "log-trace"]

        if Version(self.version) >= "247.1":
            unrelated.append("oomd")
        if Version(self.version) >= "248.1":
            unrelated.extend(["sysext", "nscd"])
        if Version(self.version) >= "251.1":
            unrelated.append("link-boot-shared")
        if Version(self.version) >= "252.1":
            unrelated.append("link-journalctl-shared")
        if Version(self.version) < "254.7":
            unrelated.extend(["gnu-efi", "valgrind"])
        else:
            unrelated.extend(["passwdqc", "bootloader", "link-portabled-shared"])

        for opt in unrelated:
            tc.project_options[opt] = "false"

        # 'rootprefix' is unused during libsystemd packaging but systemd > v247
        # build files require 'prefix' to be a subdirectory of 'rootprefix'.
        tc.project_options["rootprefix"] = self.package_folder

        # There are a few places in libsystemd where pkgconfig dependencies are
        # not used in compile time and only used in link time. And because of
        # that it is not enough to use the 'PkgConfigDeps' generator here. It
        # is also required to provide a path to the header files directly to
        # the compiler.
        for dependency in self.dependencies.values():
            for includedir in dependency.cpp_info.aggregated_components().includedirs:
                tc.c_args.append(f"-I{includedir}")

        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        meson_build = os.path.join(self.source_folder, "meson.build")
        replace_in_file(self, meson_build, "@CONAN_SRC_REL_PATH@", f"'../{self.source_path.name}'")

    def build(self):
        self._patch_sources()

        meson = Meson(self)
        meson.configure()
        systemd_target = ("systemd:shared_library" if self.options.shared
                  else "systemd:static_library")
        udev_target = ("udev:shared_library" if self.options.shared
                  else "udev:static_library")
        meson.build(target=f"version.h {systemd_target} {udev_target}")

    def package(self):
        copy(self, "LICENSE.LGPL2.1", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", os.path.join(self.source_folder, "src", "systemd"),
             os.path.join(self.package_folder, "include", "systemd"))
        copy(self, "libudev.h", os.path.join(self.source_folder, "src", "libudev"),
             os.path.join(self.package_folder, "include"))

        if self.options.shared:
            copy(self, "libsystemd.so", self.build_folder,
                 os.path.join(self.package_folder, "lib"))
            copy(self, "libsystemd.so.{}".format(self._so_version.split('.')),
                 self.build_folder, os.path.join(self.package_folder, "lib"))
            copy(self, f"libsystemd.so.{self._so_version}",
                 self.build_folder, os.path.join(self.package_folder, "lib"))
            copy(self, "libudev.so", self.build_folder, os.path.join(self.package_folder, "lib"))
            copy(self, "libudev.so.*", self.build_folder, os.path.join(self.package_folder, "lib"))
        else:
            copy(self, "libsystemd.a", self.build_folder,
                 os.path.join(self.package_folder, "lib"))
            copy(self, "libudev.a", self.build_folder,
                 os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.components["libsystemd"].libs = ["systemd"]
        self.cpp_info.components["libsystemd"].requires = ["libcap::cap", "libmount::libmount"]
        if Version(self.version) >= "253.6":
            self.cpp_info.components["libsystemd"].requires.append("libxcrypt::libxcrypt")
        if self.options.with_selinux:
            self.cpp_info.components["libsystemd"].requires.append("libselinux::selinux")
        if self.options.with_lz4:
            self.cpp_info.components["libsystemd"].requires.append("lz4::lz4")
        if self.options.with_xz:
            self.cpp_info.components["libsystemd"].requires.append("xz_utils::xz_utils")
        if self.options.with_zstd:
            self.cpp_info.components["libsystemd"].requires.append("zstd::zstdlib")
        self.cpp_info.components["libsystemd"].set_property("pkg_config_name", "libsystemd")
        self.cpp_info.components["libsystemd"].set_property("component_version", str(Version(self.version).major))
        self.cpp_info.components["libsystemd"].system_libs = ["rt", "pthread", "dl"]

        # TODO: to remove in conan v2
        self.cpp_info.components["libsystemd"].version = str(Version(self.version).major)

        self.cpp_info.components["libudev"].libs = ["udev"]
        self.cpp_info.components["libudev"].requires = ["libcap::cap"]
        self.cpp_info.components["libudev"].set_property("pkg_config_name", "libudev")
        self.cpp_info.components["libudev"].system_libs = ["rt", "pthread"]

        # TODO: to remove in conan v2
        self.cpp_info.components["libudev"].version = str(Version(self.version).major)
