from conan import ConanFile
from conan.tools import apple, files, microsoft, scm
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
from conans.tools import stdcpp_library

import functools
import os

required_conan_version = ">=1.51.3"


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
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

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
        if scm.Version(self.version) >= "4.4.0":
            if self.settings.compiler == "gcc" and scm.Version(self.settings.compiler.version) < "7":
                raise ConanInvalidConfiguration("New versions of harfbuzz require at least gcc 7")

        if self.options.with_glib and self.options["glib"].shared and microsoft.is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(
                "Linking shared glib with the MSVC static runtime is not supported"
            )

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/2.12.1")
        if self.options.with_icu:
            self.requires("icu/71.1")
        if self.options.with_glib:
            self.requires("glib/2.73.3")

    def layout(self):
        return basic_layout(self, src_folder="source_subfolder")

    def generate(self):
        def is_enabled(value):
            return "enabled" if value else "disabled"

        deps = PkgConfigDeps(self)
        deps.generate()

        tc = MesonToolchain(self)
        tc.project_options.update({
            "freetype": is_enabled(self.options.with_freetype),
            "graphite2": is_enabled(False),
            "glib": is_enabled(self.options.with_glib),
            "icu": is_enabled(self.options.with_icu),
            "tests": is_enabled(False),
            "docs": is_enabled(False)
        })
        if apple.is_apple_os(self):
            tc.project_options["coretext"] = is_enabled(True)
        elif self.settings.os == "Windows":
            tc.project_options["gdi"] = is_enabled(self.options.with_gdi)
            tc.project_options["directwrite"] = is_enabled(self.options.with_directwrite)
        if self.settings.compiler == "gcc" and self.settings.os == "Windows":
            tc.c_args = ["-Wa", "-mbig-obj"]
            tc.cpp_args = ["-Wa", "-mbig-obj"]

        tc.generate()

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_meson(self):
        meson = Meson(self)
        meson.configure()
        return meson

    def build(self):
        files.apply_conandata_patches(self)
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self.source_folder)
        meson = self._configure_meson()
        meson.install()
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "harfbuzz"
        self.cpp_info.names["cmake_find_package_multi"] = "harfbuzz"
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
        if apple.is_apple_os(self):
            self.cpp_info.frameworks.extend(["CoreFoundation", "CoreGraphics", "CoreText"])
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)

    def package_id(self):
        if self.options.with_glib and not self.options["glib"].shared:
            self.info.requires["glib"].full_package_mode()
