import os
import shutil
import glob

from conans import ConanFile, tools, Meson, VisualStudioBuildEnvironment
from conans.errors import ConanInvalidConfiguration

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

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.options.with_xft == "auto":
            self.options.with_xft = self.settings.os in ["Linux", "FreeBSD"]
        if self.options.with_freetype == "auto":
            self.options.with_freetype = not self.settings.os in ["Windows", "Macos"]
        if self.options.with_fontconfig == "auto":
            self.options.with_fontconfig = not self.settings.os in ["Windows", "Macos"]

        if self.options.with_xft and not self.settings.os in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("Xft can only be used on Linux and FreeBSD")

        if self.options.with_xft and (not self.options.with_freetype or not self.options.with_fontconfig):
            raise ConanInvalidConfiguration("Xft requires freetype and fontconfig")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.3")
        self.build_requires("meson/0.56.2")

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/2.10.4")

        if self.options.with_fontconfig:
            self.requires("fontconfig/2.13.92")
        if self.options.with_xft:
            self.requires("xorg/system")
        if self.options.with_cairo:
            self.requires("cairo/1.17.4")
        self.requires("harfbuzz/2.7.4")
        self.requires("glib/2.67.1")
        self.requires("fribidi/1.0.9")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extrated_dir = self.name + "-" + self.version
        os.rename(extrated_dir, self._source_subfolder)

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
        self.cpp_info.components['pango_'].libs = ['pango-1.0']
        self.cpp_info.components['pango_'].names['pkg_config'] = 'pango'
        if self.settings.os == "Linux":
            self.cpp_info.components['pango_'].system_libs.append("m")
        self.cpp_info.components['pango_'].requires.append('glib::glib-2.0')
        self.cpp_info.components['pango_'].requires.append('glib::gobject-2.0')
        self.cpp_info.components['pango_'].requires.append('glib::gio-2.0')
        self.cpp_info.components['pango_'].requires.append('fribidi::fribidi')
        self.cpp_info.components['pango_'].requires.append('harfbuzz::harfbuzz')
        if self.options.with_fontconfig:
            self.cpp_info.components['pango_'].requires.append('fontconfig::fontconfig')


        if self.options.with_xft:
            self.cpp_info.components['pango_'].requires.append('xorg::xft')
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
