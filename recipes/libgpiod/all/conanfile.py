import os

from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps, AutotoolsDeps
from conan.tools.env import VirtualBuildEnv
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy, rmdir, rm
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.54.0"

class LibgpiodConan(ConanFile):
    name = "libgpiod"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/"
    license = "LGPL-2.1-or-later"
    description = "C library and tools for interacting with the linux GPIO character device"
    topics = ("gpio", "libgpiod", "libgpiodcxx", "linux")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
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

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("libgpiod supports only Linux")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.enable_bindings_cxx:
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        self.requires("linux-headers-generic/5.13.9")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.6")
        self.tool_requires("pkgconf/1.7.4")
        self.tool_requires("autoconf-archive/2022.09.03")
        self.tool_requires("linux-headers-generic/5.13.9")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
    
    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        yes_no = lambda v: "yes" if v else "no"
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend({
            "--enable-bindings-cxx={}".format(yes_no(self.options.enable_bindings_cxx)),
            "--enable-tools={}".format(yes_no(self.options.enable_tools))
        })
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["gpiod"].libs = ["gpiod"]
        self.cpp_info.components["gpiod"].names["pkg_config"] = "gpiod"
        if self.options.enable_bindings_cxx:
            self.cpp_info.components["gpiodcxx"].libs = ["gpiodcxx"]
            self.cpp_info.components["gpiodcxx"].names["pkg_config"] = "gpiodcxx"
            self.cpp_info.components["gpiodcxx"].requires = ["gpiod"]
