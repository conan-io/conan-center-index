from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"


class KModConan(ConanFile):
    name = "kmod"
    description = "linux kernel module handling library"
    topics = ("libkmod", "linux", "kernel", "module")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kmod-project/kmod"
    license = "LGPL-2.1-only"
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_zstd": [True, False],
        "with_xz": [True, False],
        "with_zlib": [True, False],
        "with_openssl": [True, False],
        "experimental": [True, False],
        "logging": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_zstd": True,
        "with_xz": True,
        "with_zlib": True,
        "with_openssl": True,
        "experimental": False,
        "logging": False,
    }

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")
        if self.options.with_xz:
            self.requires("xz_utils/5.4.2")
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
        if self.options.with_openssl:
            self.requires("openssl/3.1.0")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("kmod is Linux-only!")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        yes_no = lambda v: "yes" if v else "no"
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--with-zstd=%s" % yes_no(self.options.with_zstd))
        tc.configure_args.append("--with-xz=%s" % yes_no(self.options.with_xz))
        tc.configure_args.append("--with-zlib=%s" % yes_no(self.options.with_zlib))
        tc.configure_args.append("--with-openssl=%s" % yes_no(self.options.with_openssl))
        tc.configure_args.append("--enable-experimental=%s" % yes_no(self.options.experimental))
        tc.configure_args.append("--enable-logging=%s" % yes_no(self.options.logging))
        tc.configure_args.append("--enable-debug=%s" % yes_no(self.settings.build_type == "Debug"))
        tc.configure_args.append("--enable-tools=no")
        tc.configure_args.append("--enable-manpages=no")
        tc.configure_args.append("--enable-test-modules=no")
        tc.configure_args.append("--enable-python=no")
        tc.configure_args.append("--enable-coverage=no")
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
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libkmod")
        self.cpp_info.libs = ["kmod"]
        self.cpp_info.system_libs = ["pthread"]
