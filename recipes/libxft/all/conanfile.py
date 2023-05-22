from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout

import os

required_conan_version = ">=1.53.0"

class libxftConan(ConanFile):
    name = "libxft"
    description = 'X FreeType library'
    topics = ("x11", "xorg")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.x.org/wiki/"
    license = "X11"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("xorg/system")
        self.requires("freetype/2.13.0")
        self.requires("fontconfig/2.14.2")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        self.tool_requires("libtool/2.4.7")
        self.tool_requires("xorg-macros/1.19.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install(args=["-j1"])
        rm(self, "*.la", f"{self.package_folder}/lib", recursive=True)
        rmdir(self, f"{self.package_folder}/lib/pkgconfig")
        rmdir(self, f"{self.package_folder}/share")

    def package_info(self):
        self.cpp_info.names['pkg_config'] = "Xft"
        self.cpp_info.set_property("pkg_config_name", "xft")
        self.cpp_info.libs = ["Xft"]
