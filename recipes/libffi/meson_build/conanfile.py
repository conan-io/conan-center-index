from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, mkdir, replace_in_file, rm, rmdir
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import glob
import os
import shutil
import sys

required_conan_version = ">=1.57.0"


class LibffiConan(ConanFile):
    name = "libffi"
    description = "A portable, high level programming interface to various calling conventions"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceware.org/libffi/"
    topics = ("runtime", "foreign-function-interface", "runtime-library")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "structs": [True, False],
        "raw_api": [True, False],
        "purify_safety": [True, False],
        "pax_emutramp": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "structs": True,
        "raw_api": True,
        "purify_safety": False,
        "pax_emutramp": False
    }

    def export_sources(self):
        pass

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.requires("meson/1.4.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        tc = MesonToolchain(self)
        tc.preprocessor_definitions['structs'] = 'true' if self.options.structs else 'false'
        tc.preprocessor_definitions['raw_api'] = 'true' if self.options.raw_api else 'false'
        tc.preprocessor_definitions['purify_safety'] = 'true' if self.options.purify_safety else 'false'
        tc.preprocessor_definitions['pax_emutramp'] = 'true' if self.options.pax_emutramp else 'false'
        tc.preprocessor_definitions['ffi-debug'] = 'true' if self.settings.build_type == "Debug" else "false"
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        meson = Meson(self)
        meson.install()

    def package_info(self):
        self.cpp_info.components["libffi"].set_property("pkg_config_name", "libffi")
        self.cpp_info.components["libffi"].libs = ["ffi"]
