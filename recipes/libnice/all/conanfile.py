import os
from conan import ConanFile
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.files import copy, get, rmdir
from conan.tools.layout import basic_layout
from conan.tools.gnu import PkgConfigDeps


class LibniceConan(ConanFile):
    name = "libnice"
    version = "0.1.19"
    homepage = "https://libnice.freedesktop.org/"
    license = "MPL-1.1 AND LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    description = "a GLib ICE implementation"
    topics = ("ice", "stun", "turn")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/2.75.0")

    def build_requirements(self):
        self.build_requires("meson/0.64.1")
        self.build_requires("pkgconf/1.9.3")
        self.build_requires("glib/2.75.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = MesonToolchain(self)
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, pattern="COPYING*", dst=os.path.join(self.package_folder,
             "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["libnice"]
