from conan import ConanFile
from conan.tools import files
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.57.0"

class LibgpiodConan(ConanFile):
    name = "libgpiod"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/"
    license = "LGPL-2.1-or-later"
    description = "C library and tools for interacting with the linux GPIO character device"
    topics = ("gpio", "libgpiod", "libgpiodcxx", "linux")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_bindings_cxx": [True, False],
        "enable_tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_bindings_cxx": False,
        "enable_tools": False,
    }
    
    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("libgpiod supports only Linux")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.enable_bindings_cxx:
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        self.build_requires("pkgconf/1.7.4")
        self.build_requires("autoconf-archive/2021.02.19")
        self.build_requires("linux-headers-generic/5.13.9")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.append("--enable-shared={}".format(yes_no(self.options.shared)))
        tc.configure_args.append("--enable-static={}".format(yes_no(not self.options.shared)))
        tc.configure_args.append("--enable-bindings-cxx={}".format(yes_no(self.options.enable_bindings_cxx)))
        tc.configure_args.append("--enable-tools={}".format(yes_no(self.options.enable_tools)))
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        files.copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        files.rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["gpiod"].libs = ["gpiod"]
        self.cpp_info.components["gpiod"].names["pkg_config"] = "gpiod"
        if self.options.enable_bindings_cxx:
            self.cpp_info.components["gpiodcxx"].libs = ["gpiodcxx"]
            self.cpp_info.components["gpiodcxx"].names["pkg_config"] = "gpiodcxx"
            self.cpp_info.components["gpiodcxx"].requires = ["gpiod"]
