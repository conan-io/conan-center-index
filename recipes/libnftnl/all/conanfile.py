import os

from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.files import copy, get, rmdir, rm
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.53.0"

class LibnftnlConan(ConanFile):
    name = "libnftnl"
    license = "GPL-2-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://netfilter.org/projects/libnftnl/index.html"
    description = "Library providing a low-level netlink programming interface (API) to the in-kernel nf_tables subsystem"
    topics = ("libnftnl", "netlink", "nftables")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    package_type = "library"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libmnl/1.0.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def configure(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("libnftnl is only supported on Linux")
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
    
    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["nftnl"]