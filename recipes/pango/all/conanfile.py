import os
import glob

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import PkgConfigDeps
from conan.tools.files import (
    copy,
    get,
    rename,
    rm,
    replace_in_file,
    rmdir
)
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class PangoConan(ConanFile):
    name = "pango"
    license = "LGPL-2.0-and-later"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Internationalized text layout and rendering library"
    homepage = "https://www.pango.org/"
    topics = ("fontconfig", "fonts", "freedesktop")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libthai": [True, False],
        "with_cairo": [True, False],
        "with_xft": [True, False, "auto"],
        "with_freetype": [True, False, "auto"],
        "with_fontconfig": [True, False, "auto"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libthai": False,
        "with_cairo": True,
        "with_xft": "auto",
        "with_freetype": "auto",
        "with_fontconfig": "auto"
    }
    generators = "pkg_config"

    def validate(self):
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(
                "this recipe does not support GCC before version 5. contributions are welcome")
        if self.options.with_xft and not self.settings.os in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("Xft can only be used on Linux and FreeBSD")

        if self.options.with_xft and (not self.options.with_freetype or not self.options.with_fontconfig):
            raise ConanInvalidConfiguration("Xft requires freetype and fontconfig")

        if self.options["glib"].shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Linking shared glib against static MSVC runtime is not supported")

        if self.options.shared and (not self.options["glib"].shared
                                    or not self.options["harfbuzz"].shared or
                                    (self.options.with_cairo
                                     and not self.options["cairo"].shared)):
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

        if self.options.with_xft == "auto":
            self.options.with_xft = self.settings.os in ["Linux", "FreeBSD"]
        if self.options.with_freetype == "auto":
            self.options.with_freetype = not self.settings.os in ["Windows", "Macos"]
        if self.options.with_fontconfig == "auto":
            self.options.with_fontconfig = not self.settings.os in ["Windows", "Macos"]
        if self.options.shared:
            self.options["glib"].shared = True
            self.options["harfbuzz"].shared = True
            if self.options.with_cairo:
                self.options["cairo"].shared = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        def is_enabled(option):
            return "enabled" if option else "disabled"

        pkg_deps = PkgConfigDeps(self)
        pkg_deps.generate()

        meson = MesonToolchain(self)
        meson.project_options.update({
            "introspection": is_enabled(False),
            "libthai": is_enabled(self.options.with_libthai),
            "cairo": is_enabled(self.options.with_cairo),
            "xft": is_enabled(self.options.with_xft),
            "fontconfig": is_enabled(self.options.with_fontconfig),
            "freetype": is_enabled(self.options.with_freetype)
        })
        meson.generate()

        env = VirtualBuildEnv(self)
        env.generate()

    def build_requirements(self):
        self.tool_requires("pkgconf/1.9.3")
        self.tool_requires("meson/0.64.1")

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/2.12.1")

        if self.options.with_fontconfig:
            self.requires("fontconfig/2.13.93")
        if self.options.with_xft:
            self.requires("libxft/2.3.6")
        if self.options.with_xft and self.options.with_fontconfig and self.options.with_freetype:
            self.requires("xorg/system")    # for xorg::xrender
        if self.options.with_cairo:
            self.requires("cairo/1.17.4")
        self.requires("harfbuzz/6.0.0")
        self.requires("glib/2.75.0")
        self.requires("fribidi/1.0.12")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self.source_folder)

    def build(self):
        meson_build = os.path.join(self.source_folder, "meson.build")
        replace_in_file(self, meson_build, "subdir('tests')", "")
        replace_in_file(self, meson_build, "subdir('tools')", "")
        replace_in_file(self, meson_build, "subdir('utils')", "")
        replace_in_file(self, meson_build, "subdir('examples')", "")
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        def rename_msvc_libs():
            lib_folder = os.path.join(self.package_folder, "lib")
            for filename_old in glob.glob(os.path.join(lib_folder, "*.a")):
                filename_new = filename_old[3:-2] + ".lib"
                self.output.info(f"rename {filename_old} into {filename_new}")
                rename(self, filename_old, filename_new)

        meson = Meson(self)
        meson.install()
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            rename_msvc_libs()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "pango-all-do-no-use")

        self.cpp_info.components["pango_"].set_property("pkg_config_name", "pango")
        self.cpp_info.components["pango_"].libs = ["pango-1.0"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["pango_"].system_libs.append("m")
        self.cpp_info.components["pango_"].requires.append("glib::glib-2.0")
        self.cpp_info.components["pango_"].requires.append("glib::gobject-2.0")
        self.cpp_info.components["pango_"].requires.append("glib::gio-2.0")
        self.cpp_info.components["pango_"].requires.append("fribidi::fribidi")
        self.cpp_info.components["pango_"].requires.append("harfbuzz::harfbuzz")

        if self.options.with_fontconfig:
            self.cpp_info.components["pango_"].requires.append("fontconfig::fontconfig")

        if self.options.with_xft:
            self.cpp_info.components["pango_"].requires.append("libxft::libxft")
            # Pango only uses xrender when Xft, fontconfig and freetype are enabled
            if self.options.with_fontconfig and self.options.with_freetype:
                self.cpp_info.components["pango_"].requires.append("xorg::xrender")
        if self.options.with_cairo:
            self.cpp_info.components["pango_"].requires.append("cairo::cairo_")
        self.cpp_info.components["pango_"].includedirs = [os.path.join(self.package_folder, "include", "pango-1.0")]

        if self.options.with_freetype:
            self.cpp_info.components["pangoft2"].set_property("pkg_config_name", "pangoft2")
            self.cpp_info.components["pangoft2"].libs = ["pangoft2-1.0"]
            self.cpp_info.components["pangoft2"].requires = ["pango_", "freetype::freetype"]
            self.cpp_info.components["pangoft2"].includedirs = [os.path.join(self.package_folder, "include", "pango-1.0")]

        if self.options.with_fontconfig:
            self.cpp_info.components["pangofc"].set_property("pkg_config_name", "pangofc")
            if self.options.with_freetype:
                self.cpp_info.components["pangofc"].requires = ["pangoft2"]

        if self.settings.os != "Windows":
            self.cpp_info.components["pangoroot"].set_property("pkg_config_name", "pangoroot")
            if self.options.with_freetype:
                self.cpp_info.components["pangoroot"].requires = ["pangoft2"]

        if self.options.with_xft:
            self.cpp_info.components["pangoxft"].set_property("pkg_config_name", "pangoxft")
            self.cpp_info.components["pangoxft"].libs = ["pangoxft-1.0"]
            self.cpp_info.components["pangoxft"].requires = ["pango_", "pangoft2"]
            self.cpp_info.components["pangoxft"].includedirs = [os.path.join(self.package_folder, "include", "pango-1.0")]

        if self.settings.os == "Windows":
            self.cpp_info.components["pangowin32"].set_property("pkg_config_name", "pangowin32")
            self.cpp_info.components["pangowin32"].libs = ["pangowin32-1.0"]
            self.cpp_info.components["pangowin32"].requires = ["pango_"]
            self.cpp_info.components["pangowin32"].system_libs.append("gdi32")

        if self.options.with_cairo:
            self.cpp_info.components["pangocairo"].set_property("pkg_config_name", "pangocairo")
            self.cpp_info.components["pangocairo"].libs = ["pangocairo-1.0"]
            self.cpp_info.components["pangocairo"].requires = ["pango_"]
            if self.options.with_freetype:
                self.cpp_info.components["pangocairo"].requires.append("pangoft2")
            if self.settings.os == "Windows":
                self.cpp_info.components["pangocairo"].requires.append("pangowin32")
                self.cpp_info.components["pangocairo"].system_libs.append("gdi32")
            self.cpp_info.components["pangocairo"].includedirs = [os.path.join(self.package_folder, "include", "pango-1.0")]

        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

    def package_id(self):
        if not self.options["glib"].shared:
            self.info.requires["glib"].full_package_mode()
