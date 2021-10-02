from conans import ConanFile, tools, Meson, VisualStudioBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import functools
import glob
import os
import shutil

required_conan_version = ">=1.33.0"


class PangoConan(ConanFile):
    name = "pango"
    license = "LGPL-2.0-and-later"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Internationalized text layout and rendering library"
    homepage = "https://www.pango.org/"
    topics = ("text", "layout", "font", "rendering")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libthai": [True, False],
        "with_cairo": [True, False],
        "with_xft": [True, False],
        "with_freetype": [True, False],
        "with_fontconfig": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libthai": False,
        "with_cairo": True,
        "with_xft": True,
        "with_freetype": True,
        "with_fontconfig": True,
    }

    generators = "pkg_config"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        self.options.with_freetype = self.settings.os not in ("Windows", "Macos")
        self.options.with_fontconfig = self.settings.os not in ("Windows", "Macos")
        if self.settings.os not in ("FreeBSD", "Linux"):
            del self.options.with_xft

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/2.11.0")
        if self.options.with_fontconfig:
            self.requires("fontconfig/2.13.93")
        if self.options.get_safe("with_xft"):
            self.requires("xorg/system")
        if self.options.with_cairo:
            self.requires("cairo/1.17.4")
        self.requires("harfbuzz/2.9.1")
        self.requires("glib/2.70.0")
        self.requires("fribidi/1.0.10")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")
        self.build_requires("meson/0.59.1")

    def validate(self):
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("this recipe does not support GCC before version 5. contributions are welcome")

        if self.options.with_freetype and not self.options.with_fontconfig:
            raise ConanInvalidConfiguration(f"{self.name}:with_freetype=True requires {self.name}:with_fontconfig=True")

        if self.options.get_safe("with_xft") and (not self.options.with_freetype or not self.options.with_fontconfig):
            raise ConanInvalidConfiguration(f"{self.name}:with_xft=True requires {self.name}:with_freetype=True and {self.name}:with_fontconfig=True")

        if self.options.with_freetype and not self.options["cairo"].with_freetype:
            raise ConanInvalidConfiguration(f"{self.name}:with_freetype=True requires cairo:with_freetype=True")

        if tools.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("cross building is not supported (due to missing conan Meson cross building support)")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_meson(self):
        meson = Meson(self)
        meson.options["introspection"] = "disabled"
        meson.options["libthai"] = "enabled" if self.options.with_libthai else "disabled"
        meson.options["cairo"] = "enabled" if self.options.with_cairo else "disabled"
        meson.options["xft"] = "enabled" if self.options.get_safe("with_xft") else "disabled"
        meson.options["fontconfig"] = "enabled" if self.options.with_fontconfig else "disabled"
        meson.options["freetype"] = "enabled" if self.options.with_freetype else "disabled"
        meson.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder, args=["--wrap-mode=nofallback"])
        return meson

    def build(self):
        meson_build = os.path.join(self._source_subfolder, "meson.build")
        tools.replace_in_file(meson_build, "subdir('tests')", "")
        tools.replace_in_file(meson_build, "subdir('tools')", "")
        tools.replace_in_file(meson_build, "subdir('utils')", "")
        tools.replace_in_file(meson_build, "subdir('examples')", "")
        with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if self._is_msvc else tools.no_op():
            meson = self._configure_meson()
            meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if self._is_msvc else tools.no_op():
            meson = self._configure_meson()
            meson.install()
        if self.settings.compiler == "Visual Studio":
            with tools.chdir(os.path.join(self.package_folder, "lib")):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info("rename %s into %s" % (filename_old, filename_new))
                    shutil.move(filename_old, filename_new)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(self.package_folder, "*.pdb")

    def package_info(self):
        self.cpp_info.components["pango_"].libs = ["pango-1.0"]
        self.cpp_info.components["pango_"].names["pkg_config"] = "pango"
        if self.settings.os == "Linux":
            self.cpp_info.components["pango_"].system_libs.append("m")
        self.cpp_info.components["pango_"].requires.append("glib::glib-2.0")
        self.cpp_info.components["pango_"].requires.append("glib::gobject-2.0")
        self.cpp_info.components["pango_"].requires.append("glib::gio-2.0")
        self.cpp_info.components["pango_"].requires.append("fribidi::fribidi")
        self.cpp_info.components["pango_"].requires.append("harfbuzz::harfbuzz")
        if self.options.with_fontconfig:
            self.cpp_info.components["pango_"].requires.append("fontconfig::fontconfig")

        if self.options.get_safe("with_xft"):
            self.cpp_info.components["pango_"].requires.append("xorg::xft")
            # Pango only uses xrender when Xft, fontconfig and freetype are enabled
            if self.options.with_fontconfig and self.options.with_freetype:
                self.cpp_info.components["pango_"].requires.append("xorg::xrender")
        if self.options.with_cairo:
            self.cpp_info.components["pango_"].requires.append("cairo::cairo_")
        self.cpp_info.components["pango_"].includedirs = [os.path.join(self.package_folder, "include", "pango-1.0")]

        if self.options.with_freetype:
            self.cpp_info.components["pangoft2"].libs = ["pangoft2-1.0"]
            self.cpp_info.components["pangoft2"].names["pkg_config"] = "pangoft2"
            self.cpp_info.components["pangoft2"].requires = ["pango_", "freetype::freetype"]
            self.cpp_info.components["pangoft2"].includedirs = [os.path.join(self.package_folder, "include", "pango-1.0")]

        if self.options.with_fontconfig:
            self.cpp_info.components["pangofc"].names["pkg_config"] = "pangofc"
            if self.options.with_freetype:
                self.cpp_info.components["pangofc"].requires = ["pangoft2"]

        if self.settings.os != "Windows":
            self.cpp_info.components["pangoroot"].names["pkg_config"] = "pangoroot"
            if self.options.with_freetype:
                self.cpp_info.components["pangoroot"].requires = ["pangoft2"]

        if self.options.get_safe("with_xft"):
            self.cpp_info.components["pangoxft"].libs = ["pangoxft-1.0"]
            self.cpp_info.components["pangoxft"].names["pkg_config"] = "pangoxft"
            self.cpp_info.components["pangoxft"].requires = ["pango_", "pangoft2"]
            self.cpp_info.components["pangoxft"].includedirs = [os.path.join(self.package_folder, "include", "pango-1.0")]

        if self.settings.os == "Windows":
            self.cpp_info.components["pangowin32"].libs = ["pangowin32-1.0"]
            self.cpp_info.components["pangowin32"].names["pkg_config"] = "pangowin32"
            self.cpp_info.components["pangowin32"].requires = ["pango_"]
            self.cpp_info.components["pangowin32"].system_libs.append("gdi32")

        if self.options.with_cairo:
            self.cpp_info.components["pangocairo"].libs = ["pangocairo-1.0"]
            self.cpp_info.components["pangocairo"].names["pkg_config"] = "pangocairo"
            self.cpp_info.components["pangocairo"].requires = ["pango_"]
            if self.options.with_freetype:
                self.cpp_info.components["pangocairo"].requires.append("pangoft2")
            if self.settings.os == "Windows":
                self.cpp_info.components["pangocairo"].requires.append("pangowin32")
                self.cpp_info.components["pangocairo"].system_libs.append("gdi32")
            self.cpp_info.components["pangocairo"].includedirs = [os.path.join(self.package_folder, "include", "pango-1.0")]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
