import glob
import os
import functools

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.build import cross_building, check_min_cppstd
from conan.tools.files import (
    apply_conandata_patches,
    collect_libs,
    copy,
    export_conandata_patches,
    get,
    rename,
    replace_in_file,
    rm,
    rmdir)
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.scm import Version

required_conan_version = ">=1.53"


class NvidiaVaapiDriverConan(ConanFile):
    name = "nvidia-vaapi-driver"
    description = "VA-API implementation that uses NVDEC as a backend"
    topics = ("nvidia", "vaapi")
    homepage = "https://github.com/elFarto/nvidia-vaapi-driver"
    url = "https://gitlab.com/missionrobotics/conan-packages/mr-conan-index"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
    }

    def build_requirements(self):
        self.tool_requires("meson/1.0.0")
        self.tool_requires("pkgconf/2.1.0")

    def requirements(self):
        self.requires( "nv-codec-headers/12.1.14.0" )
        self.requires( "libva/2.20.0" )
        self.requires("egl/system")

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross-building not implemented")
        if not self.options.shared:
            raise ConanInvalidConfiguration("Only shared library builds are supported")

    def layout(self):
        basic_layout(self, src_folder="src")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        


        if self.settings.compiler.cppstd:
            check_min_cppstd( self, 11 )

    def config_options(self):
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):

        tc = PkgConfigDeps(self)
        tc.generate()

        tc = MesonToolchain(self)
        tc.generate()

        tc = VirtualBuildEnv(self)
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, pattern="COPYING*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.set_property("pkg_config_name", "nvidia-vaapi-driver")



