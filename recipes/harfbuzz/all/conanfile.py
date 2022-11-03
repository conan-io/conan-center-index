from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.files import (
    copy,
    export_conandata_patches,
    get,
    rmdir
)
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version
from conans.tools import stdcpp_library

import os

required_conan_version = ">=1.52.0"


class HarfbuzzConan(ConanFile):
    name = "harfbuzz"
    description = "HarfBuzz is an OpenType text shaping engine."
    topics = ("opentype", "text", "engine")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://harfbuzz.org"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_freetype": [True, False],
        "with_icu": [True, False],
        "with_glib": [True, False],
        "with_gdi": [True, False],
        "with_uniscribe": [True, False],
        "with_directwrite": [True, False],
        "with_subset": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_freetype": True,
        "with_icu": False,
        "with_glib": True,
        "with_gdi": True,
        "with_uniscribe": True,
        "with_directwrite": False,
        "with_subset": False,
    }

    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.with_gdi
            del self.options.with_uniscribe
            del self.options.with_directwrite

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.shared and self.options.with_glib:
            self.options["glib"].shared = True

    def validate(self):
        if self.options.shared and self.options.with_glib and not self.options["glib"].shared:
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )
        if Version(self.version) >= "4.4.0":
            if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
                raise ConanInvalidConfiguration("New versions of harfbuzz require at least gcc 7")

        if self.options.with_glib and self.options["glib"].shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(
                "Linking shared glib with the MSVC static runtime is not supported"
            )

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/2.12.1")
        if self.options.with_icu:
            self.requires("icu/71.1")
        if self.options.with_glib:
            self.requires("glib/2.74.1")

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        def is_enabled(value):
            return "enabled" if value else "disabled"

        PkgConfigDeps(self).generate()

        tc = MesonToolchain(self)
        tc.project_options.update({
            "glib": is_enabled(self.options.with_glib),
            "icu": is_enabled(self.options.with_icu),
            "freetype": is_enabled(self.options.with_freetype),
            "gdi": is_enabled(self.options.get_safe("with_gdi")),
            "directwrite": is_enabled(self.options.get_safe("with_directwrite")),
            "gobject": is_enabled(can_run(self)),
            "tests": "disabled",
            "docs": "disabled",
            "benchmark": "disabled",
            "icu_builtin": "false"
        })
        tc.generate()

        VirtualBuildEnv(self).generate()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def build_requirements(self):
        self.tool_requires("meson/0.63.3")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        meson = Meson(self)
        meson.install()
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "harfbuzz"
        self.cpp_info.names["cmake_find_package_multi"] = "harfbuzz"
        self.cpp_info.set_property("pkg_config_name", "harfbuzz")
        if self.options.with_icu:
            self.cpp_info.libs.append("harfbuzz-icu")
        if self.options.with_subset:
            self.cpp_info.libs.append("harfbuzz-subset")
        self.cpp_info.libs.append("harfbuzz")
        self.cpp_info.includedirs.append(os.path.join("include", "harfbuzz"))
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.system_libs.append("user32")
            if self.options.with_gdi or self.options.with_uniscribe:
                self.cpp_info.system_libs.append("gdi32")
            if self.options.with_uniscribe or self.options.with_directwrite:
                self.cpp_info.system_libs.append("rpcrt4")
            if self.options.with_uniscribe:
                self.cpp_info.system_libs.append("usp10")
            if self.options.with_directwrite:
                self.cpp_info.system_libs.append("dwrite")
        if is_apple_os(self):
            self.cpp_info.frameworks.extend(["CoreFoundation", "CoreGraphics", "CoreText", "ApplicationServices"])
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)

    def package_id(self):
        if self.options.with_glib and not self.options["glib"].shared:
            self.info.requires["glib"].full_package_mode()
