from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import export_conandata_patches, get, copy, rm
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.system.package_manager import Apt
from glob import glob
import os
from pathlib import Path
import sys


required_conan_version = ">=1.53.0"

#
# INFO: Please, remove all comments before pushing your PR!
#


class PackageConan(ConanFile):
    name = "wxwidgets"
    description = "wxWidgets is a C++ library that lets developers create applications for Windows, macOS, " \
                  "Linux and other platforms with a single code base."
    # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    # In case not listed there, use "LicenseRef-<license-file-name>"
    license = "LicenseRef-licence.txt"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.wxwidgets.org"
    # no "conan" and project name in topics. Use topics from the upstream listed on GH
    topics = (
        "windows", 
        "macos", 
        "linux",
        "c-plus-plus",
        "gtk",
        "gui",
        "cross-platform",
        "portable",
        "x11",
        "desktop",
        "cocoa",
        "gui-framework",
        "win32",
        "cross-platform-desktop"
    )
    # package_type should usually be "library" (if there is shared option)
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "unicode": [True, False],
        "compatibility": ["2.8", "3.0", "3.1"],
        "zlib": ["off", "zlib"],
        "png": ["off", "libpng"],
        "jpeg": ["off", "libjpeg"],
        "tiff": ["off", "libtiff"],
        "expat": ["off", "expat"],
        "secretstore": [True, False],
        "aui": [True, False],
        "opengl": [True, False],
        "html": [True, False],
        "mediactrl": [True, False],  # disabled by default as wxWidgets still uses deprecated GStreamer 0.10
        "propgrid": [True, False],
        "debugreport": [True, False],
        "ribbon": [True, False],
        "richtext": [True, False],
        "sockets": [True, False],
        "stc": [True, False],
        "webview": [True, False],
        "xml": [True, False],
        "xrc": [True, False],
        "cairo": [True, False],
        "help": [True, False],
        "html_help": [True, False],
        "url": [True, False],
        "protocol": [True, False],
        "fs_inet": [True, False],
        "regex": [True, False],
        "custom_enables": ["ANY"], # comma splitted list
        "custom_disables": ["ANY"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "unicode": True,
        "compatibility": "3.0",
        "zlib": "zlib",
        "png": "libpng",
        "jpeg": "libjpeg",
        "tiff": "libtiff",
        "expat": "expat",
        "secretstore": True,
        "aui": True,
        "opengl": True,
        "html": True,
        "mediactrl": False,
        "propgrid": True,
        "debugreport": True,
        "ribbon": True,
        "richtext": True,
        "sockets": True,
        "stc": True,
        "webview": False,
        "xml": True,
        "xrc": True,
        "cairo": True,
        "help": True,
        "html_help": True,
        "url": True,
        "protocol": True,
        "fs_inet": True,
        "regex": True,
        "custom_enables": "",
        "custom_disables": ""
    }

    generators = "CMakeDeps"

    _cmake = None

    @property
    def _min_cppstd(self):
        # according to https://github.com/wxWidgets/wxWidgets/blob/master/build/cmake/options.cmake#L55
        return 98

    # no exports_sources attribute, but export_sources(self) method instead
    # this allows finer grain exportation of patches per version
    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != 'Linux':
            del self.options.cairo

    def configure(self):
        if self.settings.os == 'Linux':
            self.options["gtk/*"].version = 2

        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        # src_folder must use the same source folder name the project
        cmake_layout(self, src_folder="src")

    def system_requirements(self):
        packages = []
        if self.options.secretstore:
            packages.append('libsecret-1-dev')
        if self.options.webview:
            packages.extend(['libsoup2.4-dev',
                             'libwebkitgtk-dev'])
        if self.options.mediactrl:
            packages.extend(['libgstreamer0.10-dev',
                             'libgstreamer-plugins-base0.10-dev'])
        if self.options.get_safe('cairo'):
            packages.append('libcairo2-dev')

        if packages:
            Apt(self).install(packages)

    def requirements(self):
        # prefer self.requires method instead of requires attribute
        if self.settings.os == 'Linux':
            self.requires('xorg/system')
            self.requires('gtk/system')
            if self.options.opengl:
                self.requires('opengl/system')

            if self.options.png == 'libpng':
                self.requires('libpng/1.6.37')

    def validate(self):
        # validate the minimum cpp standard supported. For C++ projects only
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)

        # in case it does not work in another configuration, it should validated here too
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    # if another tool than the compiler or CMake is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        self.tool_requires("ninja/1.11.1")
        self.tool_requires("mawk/1.3.4-20230404")
        Apt(self).install(["gawk"])

    def source(self):
        strip_root = (sys.platform != "win32")
        get(self, **self.conan_data["sources"][self.version][sys.platform], strip_root=strip_root)

    def generate(self):
        tc = CMakeToolchain(self, generator="Ninja")
        tc.generate()

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self._package(build_type=self.settings.build_type)

    def package_info(self):
        version_tokens = self.version.split('.')
        version_major = version_tokens[0]
        version_minor = version_tokens[1]
        version_suffix_major_minor = '-%s.%s' % (version_major, version_minor)
        unicode = 'u' if self.options.unicode else ''

        # wx no longer uses a debug suffix for non-windows platforms from 3.1.3 onwards
        use_debug_suffix = False
        if self.settings.build_type == 'Debug':
            version_list = [int(part) for part in version_tokens]
            use_debug_suffix = (self.settings.os == 'Windows' or version_list < [3, 1, 3])

        debug = 'd' if use_debug_suffix else ''

        if self.settings.os == 'Linux':
            prefix = 'libwx_'
            toolkit = 'gtk2'
            version = ''
            suffix = version_suffix_major_minor + ".a"
        elif self.settings.os == 'Macos':
            prefix = 'wx_'
            toolkit = 'osx_cocoa'
            version = ''
            suffix = version_suffix_major_minor
        elif self.settings.os == 'Windows':
            toolkit = 'msw'
            if self.settings.compiler == 'msvc':
                prefix = 'wx'
                version = '%s%s' % (version_major, version_minor)
                suffix = ''
            else:
                prefix = 'wx_'
                version = ''
                suffix = version_suffix_major_minor

        def base_library_pattern(library):
            return '{prefix}base{version}{unicode}{debug}_%s{suffix}' % library

        def library_pattern(library):
            return '{prefix}{toolkit}{version}{unicode}{debug}_%s{suffix}' % library

        libs = []
        if not self.options.shared:
            regex_prefix = '' if self.settings.os == "Windows" else 'lib'
            regex_suffix = '{debug}' if self.settings.os == "Windows" else '{suffix}'
            libs.append(regex_prefix + 'wxregex{unicode}' + regex_suffix)
        libs.append('{prefix}base{version}{unicode}{debug}{suffix}')
        libs.append(library_pattern('core'))
        libs.append(library_pattern('adv'))
        if self.options.sockets:
            libs.append(base_library_pattern('net'))
        if self.options.xml:
            libs.append(base_library_pattern('xml'))
        if self.options.aui:
            libs.append(library_pattern('aui'))
        if self.options.opengl:
            libs.append(library_pattern('gl'))
        if self.options.html:
            libs.append(library_pattern('html'))
        if self.options.mediactrl:
            libs.append(library_pattern('media'))
        if self.options.propgrid:
            libs.append(library_pattern('propgrid'))
        if self.options.debugreport:
            libs.append(library_pattern('qa'))
        if self.options.ribbon:
            libs.append(library_pattern('ribbon'))
        if self.options.richtext:
            libs.append(library_pattern('richtext'))
        if self.options.stc:
            if not self.options.shared:
                scintilla_prefix = '' if self.settings.os == "Windows" else 'lib'
                scintilla_suffix = '{debug}' if self.settings.os == "Windows" else '{suffix}'
                libs.append(scintilla_prefix + 'wxscintilla' + scintilla_suffix)
            libs.append(library_pattern('stc'))
        if self.options.webview:
            libs.append(library_pattern('webview'))
        if self.options.xrc:
            libs.append(library_pattern('xrc'))
        for lib in reversed(libs):
            self.cpp_info.libs.append(lib.format(prefix=prefix,
                                                 toolkit=toolkit,
                                                 version=version,
                                                 unicode=unicode,
                                                 debug=debug,
                                                 suffix=suffix))

        self.cpp_info.defines.append('wxUSE_GUI=1')
        if self.settings.build_type == 'Debug':
            self.cpp_info.defines.append('__WXDEBUG__')
        if self.options.shared:
            self.cpp_info.defines.append('WXUSINGDLL')
        if self.settings.os == 'Linux':
            self.cpp_info.defines.append('__WXGTK__')
            self.cpp_info.system_libs.extend(['dl', 'pthread', 'SM'])
        elif self.settings.os == 'Macos':
            self.cpp_info.defines.extend(['__WXMAC__', '__WXOSX__', '__WXOSX_COCOA__'])
            for framework in ['Carbon',
                              'Cocoa',
                              'AudioToolbox',
                              'OpenGL',
                              'AVKit',
                              'AVFoundation',
                              'Foundation',
                              'IOKit',
                              'ApplicationServices',
                              'CoreText',
                              'CoreGraphics',
                              'CoreServices',
                              'CoreMedia',
                              'Security',
                              'ImageIO',
                              'System',
                              'WebKit',
                              'QuartzCore']:
                self.cpp_info.frameworks.append(framework)
        elif self.settings.os == 'Windows':
            # see cmake/init.cmake
            compiler_prefix = {'msvc': 'vc',
                               'gcc': 'gcc',
                               'clang': 'clang'}.get(str(self.settings.compiler))

            arch_suffix = '_x64' if self.settings.arch == 'x86_64' else ''
            lib_suffix = '_dll' if self.options.shared else '_lib'
            libdir = '%s%s%s' % (compiler_prefix, arch_suffix, lib_suffix)
            libdir = os.path.join('lib', libdir)
            self.cpp_info.bindirs.append(libdir)
            self.cpp_info.libdirs.append(libdir)
            self.cpp_info.defines.append('__WXMSW__')
           
            if not self.options.sockets:
                self.cpp_info.defines.append("wxNO_NET_LIB")
            if not self.options.xml:
                self.cpp_info.defines.append("wxNO_XML_LIB")
            if not self.options.regex:
                self.cpp_info.defines.append("wxNO_REGEX_LIB")
            if not self.options.html:
                self.cpp_info.defines.append("wxNO_HTML_LIB")
            if not self.options.opengl:
                self.cpp_info.defines.append("wxNO_GL_LIB")
            if not self.options.debugreport:
                self.cpp_info.defines.append("wxNO_QA_LIB")
            if not self.options.xrc:
                self.cpp_info.defines.append("wxNO_XRC_LIB")
            if not self.options.aui:
                self.cpp_info.defines.append("wxNO_AUI_LIB")
            if not self.options.propgrid:
                self.cpp_info.defines.append("wxNO_PROPGRID_LIB")
            if not self.options.ribbon:
                self.cpp_info.defines.append("wxNO_RIBBON_LIB")
            if not self.options.richtext:
                self.cpp_info.defines.append("wxNO_RICHTEXT_LIB")
            if not self.options.mediactrl:
                self.cpp_info.defines.append("wxNO_MEDIA_LIB")
            if not self.options.stc:
                self.cpp_info.defines.append("wxNO_STC_LIB")
            if not self.options.webview:
                self.cpp_info.defines.append("wxNO_WEBVIEW_LIB")

            if self.options.zlib == 'off':
                self.cpp_info.defines.append("wxNO_ZLIB_LIB")
            if self.options.png == "off":
                self.cpp_info.defines.append("wxNO_PNG_LIB")
            if self.options.jpeg == "off":
                self.cpp_info.defines.append("wxNO_JPEG_LIB")
            if self.options.tiff == "off":
                self.cpp_info.defines.append("wxNO_TIFF_LIB")

            self.cpp_info.system_libs.extend(['kernel32',
                                       'user32',
                                       'gdi32',
                                       'comdlg32',
                                       'winspool',
                                       'shell32',
                                       'comctl32',
                                       'ole32',
                                       'oleaut32',
                                       'imm32',
                                       'uuid',
                                       'wininet',
                                       'rpcrt4',
                                       'winmm',
                                       'advapi32',
                                       'wsock32'])
            # Link a few libraries that are needed when using gcc on windows
            if self.settings.compiler == 'gcc':
                self.cpp_info.system_libs.extend(['uxtheme',
                                           'version',
                                           'shlwapi',
                                           'oleacc'])
        if self.settings.compiler == 'msvc':
            self.cpp_info.includedirs.append(os.path.join('include', 'msvc'))
        else:
            include_path = os.path.join("include", "wx{}".format(version_suffix_major_minor))
            self.cpp_info.includedirs = [include_path] + self.cpp_info.includedirs

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        cmake = CMake(self)

        # generic build options
        variables = {
            'wxBUILD_SHARED' : self.options.shared,
            'wxBUILD_SAMPLES' : 'OFF',
            'wxBUILD_TESTS' : 'OFF',
            'wxBUILD_DEMOS' : 'OFF',
            'wxBUILD_INSTALL' : True,
            'wxBUILD_COMPATIBILITY' : self.options.compatibility,
        }
        if self.settings.compiler == 'clang':
            variables['wxBUILD_PRECOMP'] = 'OFF'

        # platform-specific options
        if self.settings.compiler == 'msvc':
            variables['wxBUILD_USE_STATIC_RUNTIME'] = 'MT' in str(self.settings.compiler.runtime)
            variables['wxBUILD_MSVC_MULTIPROC'] = True
        if self.settings.os == 'Linux':
            # TODO : GTK3
            variables['wxBUILD_TOOLKIT'] = 'gtk2'
            variables['WXGTK3'] = 0
            variables['WXGTK2'] = 1
            variables['wxUSE_CAIRO'] = self.options.cairo
        # Disable some optional libraries that will otherwise lead to non-deterministic builds
        if self.settings.os != "Windows":
            variables['wxUSE_LIBSDL'] = 'OFF'
            variables['wxUSE_LIBICONV'] = 'OFF'
            variables['wxUSE_LIBNOTIFY'] = 'OFF'
            variables['wxUSE_LIBMSPACK'] = 'OFF'
            variables['wxUSE_LIBGNOMEVFS'] = 'OFF'

        if self.settings.os == "Windows":
            # unable to locate conan package for libpng on Windows, thus use builtin.
            variables['wxUSE_LIBPNG'] = 'builtin' if self.options.png != 'off' else 'OFF'
        else:
            # encounter link error when using builtin on Linux, thus use libpng package.
            variables['wxUSE_LIBPNG'] = 'sys' if self.options.png != 'off' else 'OFF'

        # always use builtin for packages do not support conan v2 on required version
        variables['wxUSE_LIBJPEG'] = 'builtin' if self.options.jpeg != 'off' else 'OFF'
        variables['wxUSE_LIBTIFF'] = 'builtin' if self.options.tiff != 'off' else 'OFF'
        variables['wxUSE_ZLIB'] = 'builtin' if self.options.zlib != 'off' else 'OFF'
        variables['wxUSE_EXPAT'] = 'builtin' if self.options.expat != 'off' else 'OFF'

        # wxWidgets features
        variables['wxUSE_UNICODE'] = self.options.unicode
        variables['wxUSE_SECRETSTORE'] = self.options.secretstore

        # wxWidgets libraries
        variables['wxUSE_AUI'] = self.options.aui
        variables['wxUSE_OPENGL'] = self.options.opengl
        variables['wxUSE_HTML'] = self.options.html
        variables['wxUSE_MEDIACTRL'] = self.options.mediactrl
        variables['wxUSE_PROPGRID'] = self.options.propgrid
        variables['wxUSE_DEBUGREPORT'] = self.options.debugreport
        variables['wxUSE_RIBBON'] = self.options.ribbon
        variables['wxUSE_RICHTEXT'] = self.options.richtext
        variables['wxUSE_SOCKETS'] = self.options.sockets
        variables['wxUSE_STC'] = self.options.stc
        variables['wxUSE_WEBVIEW'] = self.options.webview
        variables['wxUSE_XML'] = self.options.xml
        variables['wxUSE_XRC'] = self.options.xrc
        variables['wxUSE_HELP'] = self.options.help
        variables['wxUSE_WXHTML_HELP'] = self.options.html_help
        variables['wxUSE_URL'] = self.options.protocol
        variables['wxUSE_PROTOCOL'] = self.options.protocol
        variables['wxUSE_FS_INET'] = self.options.fs_inet
        variables['wxUSE_REGEX'] = 'builtin' if self.options.regex else 'OFF'

        for item in str(self.options.custom_enables).split(","):
            if len(item) > 0:
                variables[item] = True
        for item in str(self.options.custom_disables).split(","):
            if len(item) > 0:
                variables[item] = False

        cmake.configure(variables=variables)

        self._cmake = cmake
        return self._cmake

    def _package(self, build_type):
        copy(self, pattern="LICENSE", dst="licenses", src=os.path.join(self.source_folder, "docs"))
        cmake = self._configure_cmake()
        cmake.install(build_type=build_type)

        if self.settings.os == 'Windows':
            # copy wxrc.exe
            copy(
                self, 
                pattern='*', 
                dst=os.path.join(self.package_folder, 'bin'), 
                src=os.path.join(self.build_folder, 'bin'), 
                keep_path=False
            )
        else:
            # copy setup.h
            src_path = os.path.join(self.build_folder, 'lib')
            found = glob(os.path.join(src_path, "**", "setup.h"), recursive=True)
            if not found:
                raise ConanException(f"Missing setup.h in {src_path}")
            
            copy(
                self, 
                pattern='*setup.h', 
                dst=os.path.join(self.package_folder, 'include', 'wx'), 
                src=Path(found[0]).parent,
                keep_path=False
            )

            # make relative symlink
            bin_dir = os.path.join(self.package_folder, 'bin')
            for x in os.listdir(bin_dir):
                filename = os.path.join(bin_dir, x)
                if os.path.islink(filename):
                    target = os.readlink(filename)
                    if os.path.isabs(target):
                        rel = os.path.relpath(target, bin_dir)
                        os.remove(filename)
                        os.symlink(rel, filename)
