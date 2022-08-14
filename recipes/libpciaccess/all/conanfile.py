from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.50.0"


class LibPciAccessConan(ConanFile):
    name = "libpciaccess"
    description = "Generic PCI access library"
    topics = ("pci", "xorg")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/xorg/lib/libpciaccess"
    license = "MIT", "X11"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def validate(self):
        def is_supported(settings):
            if settings.os in ("Linux", "FreeBSD", "SunOS"):
                return True
            return settings.os == "Windows" and settings.get_safe("os.subsystem") == "cygwin"
        if not is_supported(self.settings):
            raise ConanInvalidConfiguration("Unsupported architecture.")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.6")
        self.tool_requires("pkgconf/1.7.4")
        self.tool_requires("xorg-macros/1.19.3")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()
        ms = VirtualBuildEnv(self)
        ms.generate(scope="build")

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["pciaccess"]
        self.cpp_info.set_property("pkg_config_name", "pciaccess")
