import glob
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, chdir, rmdir, rm, rename
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class PangoConan(ConanFile):
    name = "pango"
    description = "Internationalized text layout and rendering library"
    license = "LGPL-2.0-and-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.pango.org/"
    topics = ("fontconfig", "fonts", "freedesktop")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libthai": [True, False],
        "with_cairo": [True, False],
        "with_xft": [True, False, "auto"],
        "with_freetype": [True, False, "auto"],
        "with_fontconfig": [True, False, "auto"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libthai": False,
        "with_cairo": True,
        "with_xft": "auto",
        "with_freetype": "auto",
        "with_fontconfig": "auto",
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.options.with_xft == "auto":
            self.options.with_xft = self.settings.os in ["Linux", "FreeBSD"]
        if self.options.with_freetype == "auto":
            self.options.with_freetype = self.settings.os != "Windows" and not is_apple_os(self)
        if self.options.with_fontconfig == "auto":
            self.options.with_fontconfig = self.settings.os != "Windows" and not is_apple_os(self)
        if self.options.shared:
            self.options["glib"].shared = True
            self.options["harfbuzz"].shared = True
            if self.options.with_cairo:
                self.options["cairo"].shared = True

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/2.13.0")
        if self.options.with_fontconfig:
            self.requires("fontconfig/2.14.2")
        if self.options.with_xft:
            self.requires("libxft/2.3.8")
        if self.options.with_xft and self.options.with_fontconfig and self.options.with_freetype:
            self.requires("xorg/system")  # for xorg::xrender
        if self.options.with_cairo:
            self.requires("cairo/1.17.6", transitive_headers=True)
        self.requires("harfbuzz/7.3.0", transitive_headers=True)
        self.requires("glib/2.76.3", transitive_headers=True)
        self.requires("fribidi/1.0.12")

    def validate(self):
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(
                "this recipe does not support GCC before version 5. contributions are welcome"
            )
        if self.options.with_xft and not self.settings.os in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("Xft can only be used on Linux and FreeBSD")

        if self.options.with_xft and not (self.options.with_freetype and self.options.with_fontconfig):
            raise ConanInvalidConfiguration("Xft requires freetype and fontconfig")

        if self.options.shared and (
            not self.dependencies["glib"].options.shared
            or not self.dependencies["harfbuzz"].options.shared
            or (self.options.with_cairo and not self.dependencies["cairo"].options.shared)
        ):
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )

    def build_requirements(self):
        self.tool_requires("pkgconf/1.9.3")
        self.tool_requires("meson/1.1.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = MesonToolchain(self)
        tc.project_options["introspection"] = "disabled"
        tc.project_options["libthai"] = "enabled" if self.options.with_libthai else "disabled"
        tc.project_options["cairo"] = "enabled" if self.options.with_cairo else "disabled"
        tc.project_options["xft"] = "enabled" if self.options.with_xft else "disabled"
        tc.project_options["fontconfig"] = "enabled" if self.options.with_fontconfig else "disabled"
        tc.project_options["freetype"] = "enabled" if self.options.with_freetype else "disabled"
        tc.generate()

    def build(self):
        for subdir in ["tests", "tools", "utils", "examples"]:
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                            f"subdir('{subdir}')", "")
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        meson = Meson(self)
        meson.install()
        if is_msvc(self):
            with chdir(self, os.path.join(self.package_folder, "lib")):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info(f"rename {filename_old} into {filename_new}")
                    rename(self, filename_old, filename_new)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        include_dir = os.path.join(self.package_folder, "include", "pango-1.0")
        main_component = self.cpp_info.components["pango_"]
        main_component.set_property("pkg_config_name", "pango")
        main_component.libs = ["pango-1.0"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            main_component.system_libs = ["m"]
        main_component.requires.append("glib::glib-2.0")
        main_component.requires.append("glib::gobject-2.0")
        main_component.requires.append("glib::gio-2.0")
        main_component.requires.append("fribidi::fribidi")
        main_component.requires.append("harfbuzz::harfbuzz")
        if self.options.with_fontconfig:
            main_component.requires.append("fontconfig::fontconfig")
        if self.options.with_xft:
            main_component.requires.append("libxft::libxft")
            # Pango only uses xrender when Xft, fontconfig and freetype are enabled
            if self.options.with_fontconfig and self.options.with_freetype:
                main_component.requires.append("xorg::xrender")
        if self.options.with_cairo:
            main_component.requires.append("cairo::cairo")
        main_component.includedirs = [include_dir]

        if self.options.with_freetype:
            pangoft2 = self.cpp_info.components["pangoft2"]
            pangoft2.libs = ["pangoft2-1.0"]
            pangoft2.set_property("pkg_config_name", "pangoft2")
            pangoft2.requires = ["pango_", "freetype::freetype"]
            pangoft2.includedirs = [include_dir]

        if self.options.with_fontconfig:
            pangofc = self.cpp_info.components["pangofc"]
            pangofc.set_property("pkg_config_name", "pangofc")
            if self.options.with_freetype:
                pangofc.requires = ["pangoft2"]

        if self.settings.os != "Windows":
            pangoroot = self.cpp_info.components["pangoroot"]
            pangoroot.set_property("pkg_config_name", "pangoroot")
            if self.options.with_freetype:
                pangoroot.requires = ["pangoft2"]

        if self.options.with_xft:
            pangoxft = self.cpp_info.components["pangoxft"]
            pangoxft.libs = ["pangoxft-1.0"]
            pangoxft.set_property("pkg_config_name", "pangoxft")
            pangoxft.requires = ["pango_", "pangoft2"]
            pangoxft.includedirs = [include_dir]

        if self.settings.os == "Windows":
            pangowin32 = self.cpp_info.components["pangowin32"]
            pangowin32.libs = ["pangowin32-1.0"]
            pangowin32.set_property("pkg_config_name", "pangowin32")
            pangowin32.requires = ["pango_"]
            pangowin32.system_libs.append("gdi32")

        if self.options.with_cairo:
            pangocairo = self.cpp_info.components["pangocairo"]
            pangocairo.libs = ["pangocairo-1.0"]
            pangocairo.set_property("pkg_config_name", "pangocairo")
            pangocairo.requires = ["pango_"]
            if self.options.with_freetype:
                pangocairo.requires.append("pangoft2")
            if self.settings.os == "Windows":
                pangocairo.requires.append("pangowin32")
                pangocairo.system_libs.append("gdi32")
            pangocairo.includedirs = [include_dir]

        # TODO: Legacy, to be removed on Conan 2.0
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
