from conans import ConanFile, AutoToolsBuildEnvironment, tools, VisualStudioBuildEnvironment
import os
import glob
import shutil


class CairoConan(ConanFile):
    name = "cairo"
    description = "Cairo is a 2D graphics library with support for multiple output devices"
    topics = ("conan", "cairo", "graphics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cairographics.org/"
    license = ("LGPL-2.1-only", "MPL-1.1")
    exports_sources = ["patches/*"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
        "fPIC": [True, False],
        "enable_ft": [True, False],
        "enable_fc": [True, False],
        "enable_xlib": [True, False],
        "enable_xlib_xrender": [True, False],
        "enable_xcb": [True, False],
        "enable_glib": [True, False]}
    default_options = {'shared': False,
        'fPIC': True,
        "enable_ft": True,
        "enable_fc": True,
        "enable_xlib": True,
        "enable_xlib_xrender": False,
        "enable_xcb": True,
        "enable_glib": True}
    generators = "pkg_config"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == 'Windows':
            del self.options.fPIC
            del self.options.enable_fc
        if self.settings.os != 'Linux':
            del self.options.enable_xlib
            del self.options.enable_xlib_xrender
            del self.options.enable_xcb

    def requirements(self):
        if self.options.enable_ft:
            self.requires("freetype/2.10.2")
        if self.settings.os != "Windows" and self.options.enable_fc:
            self.requires("fontconfig/2.13.91")
        if self.settings.os == 'Linux':
            if self.options.enable_xlib or self.options.enable_xlib_xrender or self.options.enable_xcb:
                self.requires("xorg/system")
        if self.options.enable_glib:
            self.requires("glib/2.65.1")
        self.requires("zlib/1.2.11")
        self.requires("pixman/0.40.0")
        self.requires("libpng/1.6.37")

    def build_requirements(self):
        if self.settings.os == 'Windows':
            self.build_requires('7zip/19.00')
            if "CONAN_BASH_PATH" not in os.environ:
                self.build_requires('msys2/20190524')
        self.build_requires("pkgconf/1.7.3")

    @property
    def is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

        os.rename('cairo-%s' % self.version, self._source_subfolder)
        

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self.is_msvc:
            self._build_msvc()
        else:
            self._build_configure()

    def _build_msvc(self):
        with tools.chdir(self._source_subfolder):
            # https://cairographics.org/end_to_end_build_for_win32/
            win32_common = os.path.join('build', 'Makefile.win32.common')
            tools.replace_in_file(win32_common, '-MD ', '-%s ' % self.settings.compiler.runtime)
            tools.replace_in_file(win32_common, '-MDd ', '-%s ' % self.settings.compiler.runtime)
            tools.replace_in_file(win32_common, '$(ZLIB_PATH)/lib/zlib1.lib',
                                                self.deps_cpp_info['zlib'].libs[0] + '.lib')
            tools.replace_in_file(win32_common, '$(LIBPNG_PATH)/lib/libpng16.lib',
                                                self.deps_cpp_info['libpng'].libs[0] + '.lib')
            tools.replace_in_file(win32_common, '$(FREETYPE_PATH)/lib/freetype.lib',
                                                self.deps_cpp_info['freetype'].libs[0] + '.lib')
            with tools.vcvars(self.settings):
                env_msvc = VisualStudioBuildEnvironment(self)
                env_msvc.flags.append('/FS')  # C1041 if multiple CL.EXE write to the same .PDB file, please use /FS
                with tools.environment_append(env_msvc.vars):
                    env_build = AutoToolsBuildEnvironment(self)
                    args=['-f', 'Makefile.win32']
                    args.append('CFG=%s' % str(self.settings.build_type).lower())
                    args.append('CAIRO_HAS_FC_FONT=0')
                    args.append('ZLIB_PATH=%s' % self.deps_cpp_info['zlib'].rootpath)
                    args.append('LIBPNG_PATH=%s' % self.deps_cpp_info['libpng'].rootpath)
                    args.append('PIXMAN_PATH=%s' % self.deps_cpp_info['pixman'].rootpath)
                    args.append('FREETYPE_PATH=%s' % self.deps_cpp_info['freetype'].rootpath)
                    args.append('GOBJECT_PATH=%s' % self.deps_cpp_info['glib'].rootpath)
                    
                    env_build.make(args=args)
                    env_build.make(args=['-C', os.path.join('util', 'cairo-gobject')] + args)

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            # disable build of test suite
            tools.replace_in_file(os.path.join('test', 'Makefile.am'), 'noinst_PROGRAMS = cairo-test-suite$(EXEEXT)',
                                  '')
            os.makedirs('pkgconfig')
            for pc_name in  glob.glob('%s/*.pc' % self.build_folder):
                shutil.copy(pc_name, os.path.join('pkgconfig', os.path.basename(pc_name)))
            if self.options.enable_ft:
                tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "src", "cairo-ft-font.c"),
                                      '#if HAVE_UNISTD_H', '#ifdef HAVE_UNISTD_H')

            pkg_config_path = os.path.abspath('pkgconfig')
            pkg_config_path = tools.unix_path(pkg_config_path) if self.settings.os == 'Windows' else pkg_config_path

            configure_args = ['--enable-ft' if self.options.enable_ft else '--disable-ft']
            if self.settings.os != "Windows":
                configure_args.append('--enable-fc' if self.options.enable_fc else '--disable-fc')
            if self.settings.os == 'Linux':
                configure_args.append('--enable-xlib' if self.options.enable_xlib else '--disable-xlib')
                configure_args.append('--enable-xlib_xrender' if self.options.enable_xlib_xrender else '--disable-xlib_xrender')
                configure_args.append('--enable-xcb' if self.options.enable_xcb else '--disable-xcb')
            configure_args.append('--enable-gobject' if self.options.enable_glib else '--disable-gobject')
            if self.options.shared:
                configure_args.extend(['--disable-static', '--enable-shared'])
            else:
                configure_args.extend(['--enable-static', '--disable-shared'])

            env_build = AutoToolsBuildEnvironment(self)
            if self.settings.os == 'Macos':
                env_build.link_flags.extend(['-framework CoreGraphics',
                                             '-framework CoreFoundation'])
            if str(self.settings.compiler) in ['gcc', 'clang', 'apple-clang']:
                env_build.flags.append('-Wno-enum-conversion')
            with tools.environment_append(env_build.vars):
                self.run('PKG_CONFIG_PATH=%s NOCONFIGURE=1 ./autogen.sh' % pkg_config_path)
                env_build.pic = self.options.fPIC
                env_build.configure(args=configure_args, pkg_config_paths=[pkg_config_path])
                env_build.make()
                env_build.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        if self.is_msvc:
            src = os.path.join(self._source_subfolder, 'src')
            cairo_gobject = os.path.join(self._source_subfolder, 'util', 'cairo-gobject')
            inc = os.path.join('include', 'cairo')
            self.copy(pattern="cairo-version.h", dst=inc, src=self._source_subfolder)
            self.copy(pattern="cairo-features.h", dst=inc, src=src)
            self.copy(pattern="cairo.h", dst=inc, src=src)
            self.copy(pattern="cairo-deprecated.h", dst=inc, src=src)
            self.copy(pattern="cairo-win32.h", dst=inc, src=src)
            self.copy(pattern="cairo-script.h", dst=inc, src=src)
            self.copy(pattern="cairo-ft.h", dst=inc, src=src)
            self.copy(pattern="cairo-ps.h", dst=inc, src=src)
            self.copy(pattern="cairo-pdf.h", dst=inc, src=src)
            self.copy(pattern="cairo-svg.h", dst=inc, src=src)
            self.copy(pattern="cairo-gobject.h", dst=inc, src=cairo_gobject)
            if self.options.shared:
                self.copy(pattern="*cairo.lib", dst="lib", src=src, keep_path=False)
                self.copy(pattern="*cairo.dll", dst="bin", src=src, keep_path=False)
                self.copy(pattern="*cairo-gobject.lib", dst="lib", src=cairo_gobject, keep_path=False)
                self.copy(pattern="*cairo-gobject.dll", dst="bin", src=cairo_gobject, keep_path=False)
            else:
                self.copy(pattern="*cairo-static.lib", dst="lib", src=src, keep_path=False)
                self.copy(pattern="*cairo-gobject.lib", dst="lib", src=cairo_gobject, keep_path=False)
                shutil.move(os.path.join(self.package_folder, 'lib', "cairo-static.lib"),
                            os.path.join(self.package_folder, 'lib', "cairo.lib"))

    def package_info(self):
        if not self.is_msvc and self.options.enable_glib:
            self.cpp_info.libs.append('cairo-gobject')
        self.cpp_info.libs.append('cairo')
        if self.is_msvc and not self.options.shared:
            self.cpp_info.defines.append('CAIRO_WIN32_STATIC_BUILD=1')
        self.cpp_info.includedirs.append(os.path.join('include', 'cairo'))
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(['gdi32','msimg32','user32'])
