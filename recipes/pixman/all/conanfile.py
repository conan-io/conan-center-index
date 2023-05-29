import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import (
    apply_conandata_patches, collect_libs, copy, export_conandata_patches, get,
    rename, replace_in_file, rm, rmdir
)
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class PixmanConan(ConanFile):
    name = "pixman"
    description = "Pixman is a low-level software library for pixel manipulation"
    topics = ("graphics", "compositing", "rasterization")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cairographics.org/"
    license = ("LGPL-2.1-only", "MPL-1.1")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

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

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("pixman can only be built as a static library on Windows")

    def build_requirements(self):
        self.tool_requires("meson/1.1.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = MesonToolchain(self)
        tc.project_options.update({
            "libpng": "disabled",
            "gtk": "disabled"
        })
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "subdir('test')", "")
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "subdir('demos')", "")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        lib_folder = os.path.join(self.package_folder, "lib")
        rmdir(self, os.path.join(lib_folder, "pkgconfig"))
        rm(self, "*.la", lib_folder)
        fix_apple_shared_install_name(self)
        if is_msvc(self):
            prefix = "libpixman-1"
            rename(self, os.path.join(lib_folder, f"{prefix}.a"), os.path.join(lib_folder, f"{prefix}.lib"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "pixman-1"))
        self.cpp_info.set_property("pkg_config_name", "pixman-1")
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "m"]
