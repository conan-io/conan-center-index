# TODO: verify the Conan v2 migration

import functools
import os

from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.android import android_abi
from conan.tools.apple import (
    XCRun,
    fix_apple_shared_install_name,
    is_apple_os,
    to_apple_arch,
)
from conan.tools.build import (
    build_jobs,
    can_run,
    check_min_cppstd,
    cross_building,
    default_cppstd,
    stdcpp_library,
    valid_min_cppstd,
)
from conan.tools.cmake import (
    CMake,
    CMakeDeps,
    CMakeToolchain,
    cmake_layout,
)
from conan.tools.env import (
    Environment,
    VirtualBuildEnv,
    VirtualRunEnv,
)
from conan.tools.files import (
    apply_conandata_patches,
    chdir,
    collect_libs,
    copy,
    download,
    export_conandata_patches,
    get,
    load,
    mkdir,
    patch,
    patches,
    rename,
    replace_in_file,
    rm,
    rmdir,
    save,
    symlinks,
    unzip,
)
from conan.tools.gnu import (
    Autotools,
    AutotoolsDeps,
    AutotoolsToolchain,
    PkgConfig,
    PkgConfigDeps,
)
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import (
    MSBuild,
    MSBuildDeps,
    MSBuildToolchain,
    NMakeDeps,
    NMakeToolchain,
    VCVars,
    check_min_vs,
    is_msvc,
    is_msvc_static_runtime,
    msvc_runtime_flag,
    unix_path,
    unix_path_package_info_legacy,
    vs_layout,
)
from conan.tools.scm import Version
from conan.tools.system import package_manager
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class LibSixelConan(ConanFile):
    name = "libsixel"
    description = (
        "A SIXEL encoder/decoder implementation derived from kmiya's sixel"
        " (https://github.com/saitoha/sixel)."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libsixel/libsixel"
    topics = "sixel"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_curl": [True, False],
        "with_gdk_pixbuf2": [True, False],
        "with_gd": [True, False],
        "with_jpeg": [True, False],
        "with_png": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_curl": True,
        "with_gd": False,
        "with_gdk_pixbuf2": False,
        "with_jpeg": True,
        "with_png": True,
    }

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

    def requirements(self):
        if self.options.with_curl:
            self.requires("libcurl/8.1.2")
        if self.options.with_gd:
            self.requires("libgd/2.3.3")
        if self.options.with_gdk_pixbuf2:
            self.requires("gdk-pixbuf/2.42.10")
        if self.options.with_jpeg:
            self.requires("libjpeg/9e")
        if self.options.with_png:
            self.requires("libpng/1.6.40")

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross-building not implemented")
        if is_msvc(self):
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support Visual Studio"
            )

    def build_requirements(self):
        self.tool_requires("meson/1.1.1")
        self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options = {
            "libcurl": "enabled" if self.options.with_curl else "disabled",
            "gd": "enabled" if self.options.with_gd else "disabled",
            "gdk-pixbuf2": "enabled" if self.options.with_gdk_pixbuf2 else "disabled",
            "img2sixel": "disabled",
            "sixel2png": "disabled",
            "python2": "disabled",
            "libdir": "lib",
        }
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["sixel"]
