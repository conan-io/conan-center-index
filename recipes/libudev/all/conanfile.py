import os
import tarfile

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import download, move_folder_contents, copy, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.scm import Version

required_conan_version = ">=1.50.0"


class LibUdevConan(ConanFile):
    name = "libudev"
    description = "API for enumerating and introspecting local devices"
    topics = ("udev", "devices", "enumerating")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/software/systemd/man/udev.html"
    license = "GPL-2.0-or-later AND LGPL-2.1-or-later"
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "10"
        }

    def requirements(self):
        self.requires("libcap/2.69")
        # These are not actually linked into the final library.
        self.requires("libmount/2.39.2", libs=False)
        self.requires("libxcrypt/4.4.36", libs=False)

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("libudev is only supported on Linux.")
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires {str(self.settings.compiler)} >= {minimum_version}."
            )

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        self.tool_requires("m4/1.4.19")
        self.tool_requires("gperf/3.1")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        # Extract using standard Python tools due to Conan's unzip() not handling backslashes in
        # 'units/system-systemd\x2dcryptsetup.slice', etc. correctly.
        download(self, **self.conan_data["sources"][self.version], filename="sources.tar.gz")
        with tarfile.open("sources.tar.gz", "r:gz") as tar:
            tar.extractall()
        move_folder_contents(self, os.path.join(self.source_folder, f"systemd-stable-{self.version}"), self.source_folder)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = MesonToolchain(self)
        tc.project_options["tests"] = "false"
        tc.project_options["selinux"] = "false"
        tc.project_options["lz4"] = "false"
        tc.project_options["xz"] = "false"
        tc.project_options["zstd"] = "false"
        tc.project_options["static-libudev"] = "false"

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
            "dns-over-tls", "log-trace", "oomd", "sysext", "nscd",
            "link-boot-shared", "link-journalctl-shared", "passwdqc", "bootloader",
            "link-portabled-shared"]
        for opt in unrelated:
            tc.project_options[opt] = "false"

        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        meson = Meson(self)
        meson.configure()
        meson.build(target="udev:shared_library")

    def package(self):
        copy(self, "LICENSE.GPL2", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE.LGPL2.1", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "libudev.h", os.path.join(self.source_folder, "src", "libudev"), os.path.join(self.package_folder, "include"))
        copy(self, "libudev.so*", self.build_folder, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libudev")
        self.cpp_info.set_property("component_version", str(Version(self.version).major))
        self.cpp_info.libs = ["udev"]
        self.cpp_info.system_libs = ["rt", "pthread"]
