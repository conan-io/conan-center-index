from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.48.0"


class KModConan(ConanFile):
    name = "kmod"
    description = "linux kernel module handling library"
    topics = ("kmod", "libkmod", "linux", "kernel", "module")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kmod-project/kmod"
    license = "LGPL-2.1-only"
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_zstd:
            self.requires("zstd/1.5.2")
        if self.options.with_xz:
            self.requires("xz_utils/5.2.5")
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.with_openssl:
            self.requires("openssl/3.0.5")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("kmod is Linux-only!")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        self.tool_requires("pkgconf/1.7.4")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
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
        # inject tools_require env vars in build context
        ms = VirtualBuildEnv(self)
        ms.generate(scope="build")

    def build(self):
        save(self, os.path.join(self.source_folder, "libkmod", "docs", "gtk-doc.make"), "")
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        # TODO: replace by conan.tools.files.rm (conan 1.50.0)
        tools_legacy.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libkmod")
        self.cpp_info.libs = ["kmod"]
        self.cpp_info.system_libs = ["pthread"]
