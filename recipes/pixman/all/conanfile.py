import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import (
    apply_conandata_patches, copy, export_conandata_patches, get,
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
    homepage = "https://gitlab.freedesktop.org/pixman/pixman"
    license = ("MIT")
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

    def build_requirements(self):
        self.tool_requires("meson/1.4.0")

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

        # Android armv7 build of Pixman makes use of cpu-features functionality, provided in the NDK
        if self.settings.os == "Android":
            android_ndk_home = self.conf.get("tools.android:ndk_path").replace("\\", "/")
            cpu_features_path = os.path.join(android_ndk_home, "sources", "android", "cpufeatures")
            tc.project_options.update({'cpu-features-path' : cpu_features_path})

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
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        lib_folder = os.path.join(self.package_folder, "lib")
        rmdir(self, os.path.join(lib_folder, "pkgconfig"))
        rm(self, "*.la", lib_folder)
        fix_apple_shared_install_name(self)
        if is_msvc(self) and not self.options.shared:
            prefix = "libpixman-1"
            rename(self, os.path.join(lib_folder, f"{prefix}.a"), os.path.join(lib_folder, f"{prefix}.lib"))

    def package_info(self):
        self.cpp_info.libs = ['libpixman-1'] if self.settings.os == "Windows" and not self.options.shared else ['pixman-1']
        self.cpp_info.includedirs.append(os.path.join("include", "pixman-1"))
        self.cpp_info.set_property("pkg_config_name", "pixman-1")
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "m"]
