from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, rm, rmdir, copy
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
import functools
import os

required_conan_version = ">=1.57.0"

class LibxftConan(ConanFile):
    name = "libxft"
    package_type = "library"
    description = 'X FreeType library'
    topics = ("libxft", "x11", "xorg")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.x.org/wiki/"
    license = "X11"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "PkgConfigDeps"

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("xorg/system")
        self.requires("freetype/2.13.0")
        self.requires("fontconfig/2.14.2")

    def build_requirements(self):
        self.build_requires("pkgconf/1.9.3")
        self.build_requires("xorg-macros/1.19.3")
        self.build_requires("libtool/2.4.7")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    @functools.lru_cache(1)
    def _configure_autotools(self):
        args = ["--disable-dependency-tracking"]
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])
        autotools = Autotools(self)
        autotools.configure(args=args)
        return autotools

    def build(self):
        apply_conandata_patches(self)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = self._configure_autotools()
        autotools.install(args=["-j1"])
        rm(self, "*.la", f"{self.package_folder}/lib", recursive=True)
        rmdir(self, f"{self.package_folder}/lib/pkgconfig")
        rmdir(self, f"{self.package_folder}/share")

    def package_info(self):
        self.cpp_info.names['pkg_config'] = "Xft"
        self.cpp_info.set_property("pkg_config_name", "xft")
        self.cpp_info.libs = ["Xft"]
