import os
import shutil
import glob

from conans import ConanFile, tools, Meson, VisualStudioBuildEnvironment
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.32.0"

class PangoConan(ConanFile):
    name = "pango"
    license = "LGPL-2.0-and-later"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Internationalized text layout and rendering library"
    homepage = "https://www.pango.org/"
    topics = ("conan", "fontconfig", "fonts", "freedesktop")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "with_libthai": [True, False], "with_cairo": [True, False], "with_xft": [True, False, "auto"], "with_freetype": [True, False, "auto"], "with_fontconfig": [True, False, "auto"]}
    default_options = {"shared": False, "fPIC": True, "with_libthai": False, "with_cairo": True, "with_xft": "auto", "with_freetype": "auto", "with_fontconfig": "auto"}
    generators = "pkg_config"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def validate(self):
        if self.settings.compiler == "gcc" and tools.scm.Version(self, self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("this recipe does not support GCC before version 5. contributions are welcome")
        if self.options.with_xft and not self.settings.os in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("Xft can only be used on Linux and FreeBSD")

        if self.options.with_xft and (not self.options.with_freetype or not self.options.with_fontconfig):
            raise ConanInvalidConfiguration("Xft requires freetype and fontconfig")

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
            del self.options.fPIC

        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

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

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")
        self.build_requires("meson/0.62.1")

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/2.12.1")

        if self.options.with_fontconfig:
            self.requires("fontconfig/2.13.93")
        if self.options.with_xft:
            self.requires("libxft/2.3.4")
        if self.options.with_xft and self.options.with_fontconfig and self.options.with_freetype:
            self.requires("xorg/system")    # for xorg::xrender
        if self.options.with_cairo:
            self.requires("cairo/1.17.4")
        self.requires("harfbuzz/4.3.0")
        self.requires("glib/2.73.0")
        self.requires("fribidi/1.0.12")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_meson(self):
        defs = dict()
        defs["introspection"] = "disabled"

        defs["libthai"] = "enabled" if self.options.with_libthai else "disabled"
        defs["cairo"] = "enabled" if self.options.with_cairo else "disabled"
        defs["xft"] = "enabled" if self.options.with_xft else "disabled"
        defs["fontconfig"] = "enabled" if self.options.with_fontconfig else "disabled"
        defs["freetype"] = "enabled" if self.options.with_freetype else "disabled"

        meson = Meson(self)
        meson.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder, defs=defs, args=['--wrap-mode=nofallback'])
        return meson

    def build(self):
        meson_build = os.path.join(self._source_subfolder, "meson.build")
        tools.files.replace_in_file(self, meson_build, "subdir('tests')", "")
        tools.files.replace_in_file(self, meson_build, "subdir('tools')", "")
        tools.files.replace_in_file(self, meson_build, "subdir('utils')", "")
        tools.files.replace_in_file(self, meson_build, "subdir('examples')", "")
        with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if is_msvc(self) else tools.no_op():
            meson = self._configure_meson()
            meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if is_msvc(self) else tools.no_op():
            meson = self._configure_meson()
            meson.install()
        if is_msvc(self):
            with tools.files.chdir(self, os.path.join(self.package_folder, "lib")):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info("rename %s into %s" % (filename_old, filename_new))
                    shutil.move(filename_old, filename_new)
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rm(self, self.package_folder, "*.pdb")

    def package_info(self):
        self.cpp_info.components['pango_'].libs = ['pango-1.0']
        self.cpp_info.components['pango_'].names['pkg_config'] = 'pango'
        if self.settings.os in ["Linux","FreeBSD"]:
            self.cpp_info.components['pango_'].system_libs.append("m")
        self.cpp_info.components['pango_'].requires.append('glib::glib-2.0')
        self.cpp_info.components['pango_'].requires.append('glib::gobject-2.0')
        self.cpp_info.components['pango_'].requires.append('glib::gio-2.0')
        self.cpp_info.components['pango_'].requires.append('fribidi::fribidi')
        self.cpp_info.components['pango_'].requires.append('harfbuzz::harfbuzz')
        if self.options.with_fontconfig:
            self.cpp_info.components['pango_'].requires.append('fontconfig::fontconfig')


        if self.options.with_xft:
            self.cpp_info.components['pango_'].requires.append('libxft::libxft')
            # Pango only uses xrender when Xft, fontconfig and freetype are enabled
            if self.options.with_fontconfig and self.options.with_freetype:
                self.cpp_info.components['pango_'].requires.append('xorg::xrender')
        if self.options.with_cairo:
            self.cpp_info.components['pango_'].requires.append('cairo::cairo_')
        self.cpp_info.components['pango_'].includedirs = [os.path.join(self.package_folder, "include", "pango-1.0")]

        if self.options.with_freetype:
            self.cpp_info.components['pangoft2'].libs = ['pangoft2-1.0']
            self.cpp_info.components['pangoft2'].names['pkg_config'] = 'pangoft2'
            self.cpp_info.components['pangoft2'].requires = ['pango_', 'freetype::freetype']
            self.cpp_info.components['pangoft2'].includedirs = [os.path.join(self.package_folder, "include", "pango-1.0")]

        if self.options.with_fontconfig:
            self.cpp_info.components['pangofc'].names['pkg_config'] = 'pangofc'
            if self.options.with_freetype:
                self.cpp_info.components['pangofc'].requires = ['pangoft2']

        if self.settings.os != "Windows":
            self.cpp_info.components['pangoroot'].names['pkg_config'] = 'pangoroot'
            if self.options.with_freetype:
                self.cpp_info.components['pangoroot'].requires = ['pangoft2']

        if self.options.with_xft:
            self.cpp_info.components['pangoxft'].libs = ['pangoxft-1.0']
            self.cpp_info.components['pangoxft'].names['pkg_config'] = 'pangoxft'
            self.cpp_info.components['pangoxft'].requires = ['pango_', 'pangoft2']
            self.cpp_info.components['pangoxft'].includedirs = [os.path.join(self.package_folder, "include", "pango-1.0")]

        if self.settings.os == "Windows":
            self.cpp_info.components['pangowin32'].libs = ['pangowin32-1.0']
            self.cpp_info.components['pangowin32'].names['pkg_config'] = 'pangowin32'
            self.cpp_info.components['pangowin32'].requires = ['pango_']
            self.cpp_info.components['pangowin32'].system_libs.append('gdi32')

        if self.options.with_cairo:
            self.cpp_info.components['pangocairo'].libs = ['pangocairo-1.0']
            self.cpp_info.components['pangocairo'].names['pkg_config'] = 'pangocairo'
            self.cpp_info.components['pangocairo'].requires = ['pango_']
            if self.options.with_freetype:
                self.cpp_info.components['pangocairo'].requires.append('pangoft2')
            if self.settings.os == "Windows":
                self.cpp_info.components['pangocairo'].requires.append('pangowin32')
                self.cpp_info.components['pangocairo'].system_libs.append('gdi32')
            self.cpp_info.components['pangocairo'].includedirs = [os.path.join(self.package_folder, "include", "pango-1.0")]

        self.env_info.PATH.append(os.path.join(self.package_folder, 'bin'))

    def package_id(self):
        self.info.requires["glib"].full_package_mode()
        self.info.requires["harfbuzz"].full_package_mode()
        if self.options.with_cairo:
            self.info.requires["cairo"].full_package_mode()
