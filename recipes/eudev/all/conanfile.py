from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
import os


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
        "with_libselinux": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "hwdb": False,
        "mtd_probe": False,
        "programs": True,
        "with_kmod": True,
        # todo Should be enabled by default when libblkid is packaged in CCI.
        "with_libblkid": False,
        "with_libselinux": True,
    }
    provides = "libudev"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("acl/2.3.1")
        self.requires("libcap/2.69")
        self.requires("libxslt/1.1.34")
        self.requires("linux-headers-generic/5.15.128")

        if self.options.with_kmod:
            self.requires("kmod/30")
        if self.options.with_libblkid:
            self.requires("libmount/2.39")
        if self.options.with_libselinux:
            self.requires("libselinux/3.3")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")
        if self.options.with_libblkid:
            raise ConanInvalidConfiguration(f"The with_libblkid option is not yet supported. Contributions welcome.")

    def build_requirements(self):
        self.tool_requires("gperf/3.1")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            "--sysconfdir=${prefix}/res",
            f"--enable-programs={yes_no(self.options.programs)}",
            f"--enable-blkid={yes_no(self.options.with_libblkid)}",
            f"--enable-selinux={yes_no(self.options.with_libselinux)}",
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

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["udev"]
