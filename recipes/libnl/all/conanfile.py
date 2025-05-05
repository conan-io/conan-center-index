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
    license = "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/thom311/libnl"
    topics = ("netlink")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} is only supported on Linux")

    def build_requirements(self):
        self.tool_requires("bison/3.8.2")
        self.tool_requires("flex/2.6.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["nl"].libs = ["nl-3"]
        self.cpp_info.components["nl"].includedirs = [os.path.join('include', 'libnl3')]
        self.cpp_info.components["nl"].system_libs = ["pthread", "m"]
        self.cpp_info.components["nl-route"].libs = ["nl-route-3"]
        self.cpp_info.components["nl-route"].requires = ["nl"]
        self.cpp_info.components["nl-genl"].libs = ["nl-genl-3"]
        self.cpp_info.components["nl-genl"].requires = ["nl"]
        self.cpp_info.components["nl-nf"].libs = ["nl-nf-3"]
        self.cpp_info.components["nl-nf"].requires = ["nl-route"]
        self.cpp_info.components["nl-cli"].libs = ["nl-cli-3"]
        self.cpp_info.components["nl-cli"].requires = ["nl-nf", "nl-genl"]
        self.cpp_info.components["nl-cli"].system_libs = ["dl"]
        self.cpp_info.components["nl-idiag"].libs = ["nl-idiag-3"]
        self.cpp_info.components["nl-idiag"].requires = ["nl"]
