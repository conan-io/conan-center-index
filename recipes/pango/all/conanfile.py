import os
import glob

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, rename, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.60.0 <2 || >=2.0.5"


class PangoConan(ConanFile):
    name = "pango"
    license = "LGPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Internationalized text layout and rendering library"
    homepage = "https://www.pango.org/"
    topics = ("fontconfig", "fonts", "freedesktop")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libthai": [True, False],
        "with_cairo": [True, False],
        "with_xft": [True, False],
        "with_freetype": [True, False],
        "with_fontconfig": [True, False],
        "with_introspection": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libthai": False,
        "with_cairo": True,
        "with_xft": True,
        # TODO: Currently can't actually disable this in Macos at least,
        #  it always shows up as detected in meson
        "with_freetype": True,
        "with_fontconfig": True,
        "with_introspection": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["FreeBSD", "Linux"]:
            del self.options.with_xft

        # Optional in Windows/Macos but false by default
        # https://gitlab.gnome.org/GNOME/pango/-/blob/1.54.0/meson.build#L242
        if self.settings.os in ["Macos", "Windows"]:
            self.options.with_fontconfig = False
            self.options.with_freetype = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/2.13.2")
        if self.options.with_fontconfig:
            self.requires("fontconfig/2.15.0")
        if self.options.get_safe("with_xft"):
            self.requires("libxft/2.3.8")
            self.requires("xorg/system")  # for xorg::xrender
        if self.options.with_cairo:
            # "pango/pangocairo.h" includes "cairo.h"
            self.requires("cairo/1.18.0", transitive_headers=True)
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        self.requires("fribidi/1.0.13")
        # "pango/pango-coverage.h" includes "hb.h"
        self.requires("harfbuzz/8.3.0", transitive_headers=True)

    def validate(self):
        if (
            self.settings.compiler == "gcc"
            and Version(self.settings.compiler.version) < "5"
        ):
            raise ConanInvalidConfiguration(f"{self.name} does not support GCC before version 5. Contributions are welcome.")

        if self.options.get_safe("with_xft"):
            if not self.options.with_freetype or not self.options.with_fontconfig:
                raise ConanInvalidConfiguration(f"-o=&:with_xft=True requires -o=&:with_freetype=True and -o=&:with_fontconfig=True")

        if self.dependencies["glib"].options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(
                "Linking shared glib with the MSVC static runtime is not supported"
            )

        # Can't be turned off outside Macos/Windows
        # https://gitlab.gnome.org/GNOME/pango/-/blob/1.54.0/meson.build#L240
        if self.settings.os not in ["Macos", "Windows"] and not self.options.with_fontconfig:
            raise ConanInvalidConfiguration(f"{self.ref} requires -o=&:with_fontconfig=True for {self.settings.os}")

        if (self.options.with_fontconfig and self.options.with_freetype
                and self.options.with_cairo and not self.dependencies["cairo"].options.with_fontconfig):
            raise ConanInvalidConfiguration(f"{self.ref} with -o=&:with_fontconfig=True and -o=&:with_freetype=True requires -o=cairo/*:with_fontconfig=True")

        if self.options.shared:
            if not self.dependencies["glib"].options.shared:
                raise ConanInvalidConfiguration(
                    "Linking a shared library against static glib can cause unexpected behaviour."
                )
            if not self.dependencies["harfbuzz"].options.shared:
                raise ConanInvalidConfiguration(
                    "Linking a shared library against static harfbuzz can cause unexpected behaviour."
                )
            if self.options.with_cairo and not self.dependencies["cairo"].options.shared:
                raise ConanInvalidConfiguration(
                    "Linking a shared library against static cairo can cause unexpected behaviour."
                )

    def build_requirements(self):
        self.tool_requires("glib/<host_version>")
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/1.78.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        deps = PkgConfigDeps(self)
        if self.options.with_introspection:
            # gnome.generate_gir() in Meson looks for gobject-introspection-1.0.pc
            deps.build_context_activated = ["gobject-introspection"]
        deps.generate()

        enabled_disabled = lambda opt: "enabled" if opt else "disabled"
        tc = MesonToolchain(self)
        tc.project_options["introspection"] = enabled_disabled(self.options.with_introspection)
        tc.project_options["libthai"] = enabled_disabled(self.options.with_libthai)
        tc.project_options["cairo"] = enabled_disabled(self.options.with_cairo)
        tc.project_options["xft"] = enabled_disabled(self.options.get_safe("with_xft"))
        tc.project_options["fontconfig"] = enabled_disabled(self.options.with_fontconfig)
        tc.project_options["freetype"] = enabled_disabled(self.options.with_freetype)
        tc.generate()

    def _patch_sources(self):
        meson_build = os.path.join(self.source_folder, "meson.build")
        replace_in_file(self, meson_build, "subdir('tests')", "")
        replace_in_file(self, meson_build, "subdir('tools')", "")
        replace_in_file(self, meson_build, "subdir('utils')", "")
        replace_in_file(self, meson_build, "subdir('examples')", "")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def _fix_library_names(self, path):
        if is_msvc(self):
            with chdir(self, path):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info(f"rename {filename_old} into {filename_new}")
                    rename(self, filename_old, filename_new)

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        self._fix_library_names(os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        if self.options.with_introspection:
            os.rename(os.path.join(self.package_folder, "share"),
                      os.path.join(self.package_folder, "res"))

    def package_info(self):
        self.cpp_info.components["pango_"].libs = ["pango-1.0"]
        self.cpp_info.components["pango_"].set_property("pkg_config_name", "pango")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["pango_"].system_libs.append("m")
        self.cpp_info.components["pango_"].requires.append("glib::glib-2.0")
        self.cpp_info.components["pango_"].requires.append("glib::gobject-2.0")
        self.cpp_info.components["pango_"].requires.append("glib::gio-2.0")
        self.cpp_info.components["pango_"].requires.append("fribidi::fribidi")
        self.cpp_info.components["pango_"].requires.append("harfbuzz::harfbuzz")
        if self.options.with_fontconfig:
            self.cpp_info.components["pango_"].requires.append("fontconfig::fontconfig")

        if self.options.get_safe("with_xft"):
            # Pango only uses xrender when Xft, fontconfig and freetype are enabled, which if with_xft is true,
            # means that the other options are true because they are checked in the validate() method
            self.cpp_info.components["pango_"].requires.extend(["libxft::libxft", "xorg::xrender"])
        if self.options.with_cairo:
            self.cpp_info.components["pango_"].requires.append("cairo::cairo_")
        self.cpp_info.components["pango_"].includedirs = [
            os.path.join(self.package_folder, "include", "pango-1.0")
        ]

        if self.options.with_introspection:
            self.cpp_info.components["pango_"].resdirs = ["res"]
            self.buildenv_info.append_path("GI_GIR_PATH", os.path.join(self.package_folder, "res", "gir-1.0"))
            self.buildenv_info.append_path("GI_TYPELIB_PATH", os.path.join(self.package_folder, "lib", "girepository-1.0"))
            self.env_info.GI_GIR_PATH.append(os.path.join(self.package_folder, "res", "gir-1.0"))
            self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))

        # From meson.build: "To build pangoft2, we need HarfBuzz, FontConfig and FreeType"
        if self.options.with_freetype and self.options.with_fontconfig:
            self.cpp_info.components["pangoft2"].libs = ["pangoft2-1.0"]
            self.cpp_info.components["pangoft2"].set_property("pkg_config_name", "pangoft2")
            self.cpp_info.components["pangoft2"].requires = [
                "pango_",
                "freetype::freetype",
                "fontconfig::fontconfig",
            ]
            self.cpp_info.components["pangoft2"].includedirs = [
                os.path.join(self.package_folder, "include", "pango-1.0")
            ]

            # https://gitlab.gnome.org/GNOME/pango/-/blob/1.54.0/meson.build#L320
            self.cpp_info.components["pango_"].requires.append("freetype::freetype")

        if self.options.with_fontconfig:
            self.cpp_info.components["pangofc"].set_property("pkg_config_name", "pangofc")
            if self.options.with_freetype:
                # pangoft2 is always built if pango has fontconfig and freetype support
                self.cpp_info.components["pangofc"].requires = ["freetype::freetype", "harfbuzz::harfbuzz", "pangoft2"]
        elif self.options.with_freetype:
            self.cpp_info.components["pango_"].requires.append("freetype::freetype")

        if self.settings.os != "Windows":
            self.cpp_info.components["pangoroot"].set_property("pkg_config_name", "pangoroot")
            if self.options.with_freetype:
                self.cpp_info.components["pangoroot"].requires = ["pangoft2"]

        if self.options.get_safe("with_xft"):
            self.cpp_info.components["pangoxft"].libs = ["pangoxft-1.0"]
            self.cpp_info.components["pangoxft"].set_property("pkg_config_name", "pangoxft")
            # pangoft2 is always built if pango has fontconfig and freetype support,
            # which is always true if pango has xft support enabled
            self.cpp_info.components["pangoxft"].requires = ["pango_", "pangoft2"]
            self.cpp_info.components["pangoxft"].includedirs = [
                os.path.join(self.package_folder, "include", "pango-1.0")
            ]

        if self.settings.os == "Windows":
            self.cpp_info.components["pangowin32"].libs = ["pangowin32-1.0"]
            self.cpp_info.components["pangowin32"].set_property("pkg_config_name", "pangowin32")
            self.cpp_info.components["pangowin32"].requires = ["pango_"]
            self.cpp_info.components["pangowin32"].system_libs.append("gdi32")
            if Version(self.version) >= "1.50.12":
                self.cpp_info.components["pangowin32"].system_libs.append("dwrite")

        if is_apple_os(self):
            # https://gitlab.gnome.org/GNOME/pango/-/blob/1.54.0/meson.build#L333-346
            self.cpp_info.components["pango_"].frameworks.extend(["CoreText", "CoreFoundation", "ApplicationServices"])

        if self.options.with_cairo:
            self.cpp_info.components["pangocairo"].libs = ["pangocairo-1.0"]
            self.cpp_info.components["pangocairo"].set_property("pkg_config_name", "pangocairo")
            self.cpp_info.components["pangocairo"].requires = ["pango_", "cairo::cairo_"]
            if self.options.with_freetype and self.options.with_fontconfig:
                # https://gitlab.gnome.org/GNOME/pango/-/blob/1.54.0/meson.build#L506
                self.cpp_info.components["pangocairo"].requires.append("pangoft2")
            if self.settings.os == "Windows":
                self.cpp_info.components["pangocairo"].requires.append("pangowin32")
                self.cpp_info.components["pangocairo"].system_libs.append("gdi32")
            self.cpp_info.components["pangocairo"].includedirs = [
                os.path.join(self.package_folder, "include", "pango-1.0")
            ]

        self.runenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))

        # TODO: remove the following when only Conan 2.0 is supported
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.components["pango_"].names["pkg_config"] = "pango"
        self.cpp_info.components["pangoft2"].names["pkg_config"] = "pangoft2"
        self.cpp_info.components["pangofc"].names["pkg_config"] = "pangofc"
        self.cpp_info.components["pangoroot"].names["pkg_config"] = "pangoroot"
        self.cpp_info.components["pangoxft"].names["pkg_config"] = "pangoxft"
        self.cpp_info.components["pangowin32"].names["pkg_config"] = "pangowin32"
        self.cpp_info.components["pangocairo"].names["pkg_config"] = "pangocairo"
