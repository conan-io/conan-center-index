import os
import glob

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, rename, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


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
            self.dependencies.direct_host["glib"].options.shared = True
            self.dependencies.direct_host["harfbuzz"].options.shared = True
            if self.options.with_cairo:
                self.dependencies.direct_host["cairo"].options.shared = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/2.13.0")

        if self.options.with_fontconfig:
            self.requires("fontconfig/2.14.2")
        if self.options.with_xft:
            self.requires("libxft/2.3.6")
        if (
            self.options.with_xft
            and self.options.with_fontconfig
            and self.options.with_freetype
        ):
            self.requires("xorg/system")  # for xorg::xrender
        if self.options.with_cairo:
            self.requires("cairo/1.17.6")
        self.requires("glib/2.76.2", transitive_headers=True, transitive_libs=True)
        self.requires("fribidi/1.0.12")
        self.requires("harfbuzz/7.1.0")

    def validate(self):
        if (
            self.settings.compiler == "gcc"
            and Version(self.settings.compiler.version) < "5"
        ):
            raise ConanInvalidConfiguration(f"{self.name} does not support GCC before version 5. Contributions are welcome.")
        if self.options.with_xft and not self.settings.os in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("Xft can only be used on Linux and FreeBSD")

        if self.options.with_xft and (
            not self.options.with_freetype or not self.options.with_fontconfig
        ):
            raise ConanInvalidConfiguration("Xft requires freetype and fontconfig")

        if self.options.shared and (
            not self.dependencies.direct_host["glib"].options.shared
            or not self.dependencies.direct_host["harfbuzz"].options.shared
            or (self.options.with_cairo and not self.dependencies.direct_host["cairo"].options.shared)
        ):
            raise ConanInvalidConfiguration("Linking a shared library against static glib can cause unexpected behavior.")

    def build_requirements(self):
        self.tool_requires("glib/2.76.2")
        self.tool_requires("meson/1.1.0")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()
        tc = MesonToolchain(self)
        tc.project_options["introspection"] = "disabled"
        tc.project_options["libthai"] = "enabled" if self.options.with_libthai else "disabled"
        tc.project_options["cairo"] = "enabled" if self.options.with_cairo else "disabled"
        tc.project_options["xft"] = "enabled" if self.options.with_xft else "disabled"
        tc.project_options["fontconfig"] = "enabled" if self.options.with_fontconfig else "disabled"
        tc.project_options["freetype"] = "enabled" if self.options.with_freetype else "disabled"
        tc.generate()

    def build(self):
        meson_build = os.path.join(self.source_folder, "meson.build")
        replace_in_file(self, meson_build, "subdir('tests')", "")
        replace_in_file(self, meson_build, "subdir('tools')", "")
        replace_in_file(self, meson_build, "subdir('utils')", "")
        replace_in_file(self, meson_build, "subdir('examples')", "")
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

    def package_id(self):
        if not self.dependencies.direct_host["glib"].options.shared:
            self.info.requires["glib"].full_package_mode()
        if not self.dependencies.direct_host["harfbuzz"].options.shared:
            self.info.requires["harfbuzz"].full_package_mode()
        if self.options.with_cairo and not self.dependencies.direct_host["cairo"].options.shared:
            self.info.requires["cairo"].full_package_mode()

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

        if self.options.with_xft:
            self.cpp_info.components["pango_"].requires.append("libxft::libxft")
            # Pango only uses xrender when Xft, fontconfig and freetype are enabled
            if self.options.with_fontconfig and self.options.with_freetype:
                self.cpp_info.components["pango_"].requires.append("xorg::xrender")
        if self.options.with_cairo:
            self.cpp_info.components["pango_"].requires.append("cairo::cairo_")
        self.cpp_info.components["pango_"].includedirs = [
            os.path.join(self.package_folder, "include", "pango-1.0")
        ]

        if self.options.with_freetype:
            self.cpp_info.components["pangoft2"].libs = ["pangoft2-1.0"]
            self.cpp_info.components["pangoft2"].set_property("pkg_config_name", "pangoft2")
            self.cpp_info.components["pangoft2"].requires = [
                "pango_",
                "freetype::freetype",
            ]
            self.cpp_info.components["pangoft2"].includedirs = [
                os.path.join(self.package_folder, "include", "pango-1.0")
            ]

        if self.options.with_fontconfig:
            self.cpp_info.components["pangofc"].set_property("pkg_config_name", "pangofc")
            if self.options.with_freetype:
                self.cpp_info.components["pangofc"].requires = ["pangoft2"]

        if self.settings.os != "Windows":
            self.cpp_info.components["pangoroot"].set_property("pkg_config_name", "pangoroot")
            if self.options.with_freetype:
                self.cpp_info.components["pangoroot"].requires = ["pangoft2"]

        if self.options.with_xft:
            self.cpp_info.components["pangoxft"].libs = ["pangoxft-1.0"]
            self.cpp_info.components["pangoxft"].set_property("pkg_config_name", "pangoxft")
            self.cpp_info.components["pangoxft"].requires = ["pango_", "pangoft2"]
            self.cpp_info.components["pangoxft"].includedirs = [
                os.path.join(self.package_folder, "include", "pango-1.0")
            ]

        if self.settings.os == "Windows":
            self.cpp_info.components["pangowin32"].libs = ["pangowin32-1.0"]
            self.cpp_info.components["pangowin32"].set_property("pkg_config_name", "pangowin32")
            self.cpp_info.components["pangowin32"].requires = ["pango_"]
            self.cpp_info.components["pangowin32"].system_libs.append("gdi32")

        if self.options.with_cairo:
            self.cpp_info.components["pangocairo"].libs = ["pangocairo-1.0"]
            self.cpp_info.components["pangocairo"].set_property("pkg_config_name", "pangocairo")
            self.cpp_info.components["pangocairo"].requires = ["pango_"]
            if self.options.with_freetype:
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
