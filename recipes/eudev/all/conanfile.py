import os
import re

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, load, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout


required_conan_version = ">=1.54.0"


class EudevConan(ConanFile):
    name = "eudev"
    description = "eudev is a standalone dynamic and persistent device naming support (aka userspace devfs) daemon that runs independently from the init system."
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eudev-project/eudev"
    topics = ("device", "udev")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "hwdb": [True, False],
        "mtd_probe": [True, False],
        "programs": [True, False],
        "with_kmod": [True, False],
        "with_libblkid": [True, False],
        "with_selinux": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "hwdb": False,
        "mtd_probe": False,
        "programs": True,
        "with_kmod": True,
        "with_libblkid": True,
        "with_selinux": True,
    }
    provides = "libudev"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("acl/2.3.1")
        self.requires("libcap/2.69")
        self.requires("libxslt/1.1.39")
        self.requires("linux-headers-generic/6.5.9")

        if self.options.with_kmod:
            self.requires("kmod/30")
        if self.options.with_libblkid:
            self.requires("libmount/2.39.2")
        if self.options.with_selinux:
            self.requires("libselinux/3.6")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")

    def build_requirements(self):
        self.tool_requires("gperf/3.1")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.2.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = AutotoolsToolchain(self)
        def yes_no(v):
            return "yes" if v else "no"
        tc.configure_args.extend([
            "--sysconfdir=${prefix}/res",
            f"--enable-programs={yes_no(self.options.programs)}",
            f"--enable-blkid={yes_no(self.options.with_libblkid)}",
            f"--enable-selinux={yes_no(self.options.with_selinux)}",
            f"--enable-kmod={yes_no(self.options.with_kmod)}",
            f"--enable-hwdb={yes_no(self.options.hwdb)}",
            f"--enable-mtd_probe={yes_no(self.options.mtd_probe)}",
            "--enable-manpages=no",
        ])
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    @property
    def _libudev_version_txt(self):
        return os.path.join(self.package_folder, "res", f"{self.name}-libudev-version.txt")

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        pkg_config = load(self, os.path.join(self.package_folder, "lib", "pkgconfig", "libudev.pc"))
        libudev_version = next(re.finditer("^Version: ([^\n$]+)[$\n]", pkg_config, flags=re.MULTILINE)).group(1)
        save(self, self._libudev_version_txt, libudev_version)

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["udev"]
        libudev_version = load(self, self._libudev_version_txt).strip()
        self.cpp_info.set_property("pkg_config_name", "libudev")
        self.cpp_info.set_property("system_package_version", str(libudev_version))
        pkgconfig_variables = {
            'exec_prefix': '${prefix}',
        }
        self.cpp_info.set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items()))
        self.cpp_info.requires = ["acl::acl", "libcap::cap", "libxslt::xslt", "linux-headers-generic::linux-headers-generic"]
        if self.options.with_kmod:
            self.cpp_info.requires.append("kmod::kmod")
        if self.options.with_libblkid:
            self.cpp_info.requires.append("libmount::libblkid")
        if self.options.with_selinux:
            self.cpp_info.requires.append("libselinux::selinux")

        # todo Remove this workaround for Conan v1
        self.cpp_info.set_property("component_version", str(libudev_version))
