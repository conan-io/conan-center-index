from conan import ConanFile
from conan.tools.files import get, rmdir, copy, rm
from conan.tools.layout import basic_layout
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"


class LibNlConan(ConanFile):
    name = "libnl"
    description = "A collection of libraries providing APIs to netlink protocol based Linux kernel interfaces."
    topics = ("netlink")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.infradead.org/~tgr/libnl/"
    license = "LGPL-2.1-only"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False], "shared": [True, False]}
    default_options = {"fPIC": True, "shared": False}
    build_requires = ( "flex/2.6.4", "bison/3.7.6" )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Libnl is only supported on Linux")

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib", "libnl", "cli", "cls"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib", "libnl", "cli", "qdisk"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["nl"].libs = ["nl-3"]
        self.cpp_info.components["nl"].includedirs = [os.path.join('include', 'libnl3')]
        if self.settings.os != "Windows":
            self.cpp_info.components["nl"].system_libs = ["pthread", "m"]
        self.cpp_info.components["nl-route"].libs = ["nl-route-3"]
        self.cpp_info.components["nl-route"].requires = ["nl"]
        self.cpp_info.components["nl-genl"].libs = ["nl-genl-3"]
        self.cpp_info.components["nl-genl"].requires = ["nl"]
        self.cpp_info.components["nl-nf"].libs = ["nl-nf-3"]
        self.cpp_info.components["nl-nf"].requires = ["nl-route"]
        self.cpp_info.components["nl-cli"].libs = ["nl-cli-3"]
        self.cpp_info.components["nl-cli"].requires = ["nl-nf", "nl-genl"]
        self.cpp_info.components["nl-idiag"].libs = ["nl-idiag-3"]
        self.cpp_info.components["nl-idiag"].requires = ["nl"]
