import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file
from conan.tools.scm import Version
from conan.tools.system import package_manager


class wxWidgetsConan(ConanFile):
    name = "wxwidgets"
    description = "wxWidgets is a C++ library that lets developers create applications for Windows, macOS, " \
                  "Linux and other platforms with a single code base."
    topics = ("wxwidgets", "gui", "ui")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.wxwidgets.org"
    license = "wxWidgets"
    settings = "os", "arch", "compiler", "build_type"

    options = {"shared": [True, False],
               "fPIC": [True, False],
               "unicode": [True, False],
               "compatibility": ["2.8", "3.0", "3.1", None],
               "zlib": ["off", "zlib"],
               "png": ["off", "libpng"],
               "jpeg": ["off", "libjpeg", "libjpeg-turbo", "mozjpeg"],
               "tiff": ["off", "libtiff"],
               "expat": ["off", "expat"],
               "regex": ["off", "regex"],
               "svg": ["off", "nanosvg"], # TODO: cmake currently can't find "nanosvg"
               "gtk": [2, 3, "require"],
               "secretstore": [True, False],
               "aui": [True, False],
               "opengl": [True, False],
               "html": [True, False],
               "mediactrl": [True, False],
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
               "custom_enables": ["ANY"], # comma splitted list
               "custom_disables": ["ANY"]}
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
               "regex": "regex",
               "svg": "off",
               "gtk": 3,
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
               "webview": True,
               "xml": True,
               "xrc": True,
               "cairo": True,
               "help": True,
               "html_help": True,
               "url": True,
               "protocol": True,
               "fs_inet": True,
               "custom_enables": "",
               "custom_disables": ""
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe('fPIC')
        if self.settings.os != "Linux":
            self.options.rm_safe("secretstore")
            self.options.rm_safe("cairo")
            self.options.rm_safe("gtk")
        else:
            if self.options.get_safe("gtk") == 3:
                self.options["gtk/system"].version = 3
        if self.options.compatibility > Version(self.version):
            self.options.compatibility = "3.0"

    def system_requirements(self):
        apt = package_manager.Apt(self)
        packages = []
        if self.options.secretstore and self.options.gtk != 'require':
            packages.append('libsecret-1-dev')
        if self.options.webview:
            # webkit2gtk requires libsoup
            if self.options.gtk == 2:
                packages.extend(['libsoup2.4-dev',
                                 'libwebkitgtk-dev'])
            else:
                packages.extend(['libsoup2.4-dev',
                                 'libwebkitgtk-3.0-dev'])
                # TODO: Recent distro only
                # packages.extend(['libsoup3.0-dev',
                #                  'libwebkit2gtk-4.1-dev'])
        if self.options.get_safe("cairo"):
            packages.append("libcairo2-dev")
        apt.install(packages)

        yum = package_manager.Yum(self)
        packages = []
        if self.options.webview:
            packages.append("libsoup3-devel")
            packages.append("webkit2gtk4.1-devel")
        if self.options.get_safe("cairo"):
            packages.append("cairo-devel")
        yum.install(packages)

    def build_requirements(self):
        self.tool_requires("ninja/1.11.1")
        self.tool_requires("cmake/[>=3.17]")

    def requirements(self):
        if self.settings.os == 'Linux':
            self.requires('xorg/system')
            if self.options.gtk == 'require':
                self.requires("gtk/3.24.24")
            else:
                self.requires("gtk/system")
            if self.options.opengl:
                self.requires('opengl/system')
            self.requires("xkbcommon/1.5.0")
            # TODO: Does not work right now
            # if self.options.get_safe("cairo"):
            #    self.requires("cairo/1.18.0")
            if self.options.mediactrl:
                self.requires("gstreamer/1.22.3")
                self.requires("gst-plugins-base/1.19.2")
            # TODO: CMake doesn't find libsecret right now
            if self.options.get_safe("secretstore") and self.options.gtk == "require":
                self.requires("libsecret/0.20.5")
        if self.options.png == 'libpng':
            self.requires('libpng/1.6.40')
        if self.options.jpeg == 'libjpeg':
            self.requires('libjpeg/9e')
        elif self.options.jpeg == 'libjpeg-turbo':
            self.requires('libjpeg-turbo/3.0.0')
        elif self.options.jpeg == 'mozjpeg':
            self.requires('mozjpeg/4.1.3')
        if self.options.tiff == 'libtiff':
            self.requires('libtiff/4.6.0')
        if self.options.zlib == 'zlib':
            self.requires('zlib/[>=1.2.11 <2]')
        if self.options.expat == 'expat':
            self.requires('expat/2.5.0')
        if self.options.regex == 'regex' and self.version >= '3.1.6':
            self.requires('pcre2/10.42')
        if self.options.svg == 'nanosvg' and self.version >= '3.1.7':
            self.requires('nanosvg/cci.20210904')

    def validate(self):
        if self.settings.os == 'Linux':
            if not self.dependencies.direct_host["xkbcommon"].options.with_x11:
                raise ConanInvalidConfiguration("The 'with_x11' option for the 'xkbcommon' package must be enabled")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Don't change library names when cross-compiling
        replace_in_file(self, os.path.join(self.source_folder, "build", "cmake", "functions.cmake"),
                        'set(cross_target "-${CMAKE_SYSTEM_NAME}")',
                        'set(cross_target)')
        # Don't override Conan's toolchain
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'CMAKE_OSX_DEPLOYMENT_TARGET',
                        'CMAKE_OSX_DEPLOYMENT_TARGET_IGNORED')
        # Fix for strcpy_s (fix upstream?)
        if is_apple_os(self):
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            'cmake_minimum_required(VERSION 3.0)',
                            'cmake_minimum_required(VERSION 3.0)\nadd_definitions(-D__STDC_WANT_LIB_EXT1__)')
        # expat library isn't linked?
        replace_in_file(self, os.path.join(self.source_folder, "build", "cmake", "lib", "xml", "CMakeLists.txt"),
                        '${EXPAT_LIBRARIES}',
                        'expat::expat')

    def generate(self):
        tc = CMakeToolchain(self)

        # generic build options
        tc.variables['wxBUILD_SHARED'] = self.options.shared
        tc.variables['wxBUILD_SAMPLES'] = 'OFF'
        tc.variables['wxBUILD_TESTS'] = 'OFF'
        tc.variables['wxBUILD_DEMOS'] = 'OFF'
        tc.variables['wxBUILD_INSTALL'] = True
        tc.variables['wxBUILD_COMPATIBILITY'] = 'NONE' if self.options.compatibility is None else self.options.compatibility
        if self.settings.compiler == 'clang':
            tc.variables['wxBUILD_PRECOMP'] = 'OFF'

        # platform-specific options
        if self.settings.os == 'Windows':
            tc.variables['wxBUILD_USE_STATIC_RUNTIME'] = 'MT' in str(self.settings.compiler.runtime)
            tc.variables['wxBUILD_MSVC_MULTIPROC'] = True
        if self.settings.os == 'Linux':
            tc.variables['wxBUILD_TOOLKIT'] = 'gtk2' if self.options.gtk == 2 else 'gtk3'
            tc.variables['wxUSE_CAIRO'] = self.options.cairo
        # Disable some optional libraries that will otherwise lead to non-deterministic builds
        if self.settings.os != "Windows":
            tc.variables['wxUSE_LIBSDL'] = 'OFF'
            tc.variables['wxUSE_LIBICONV'] = 'OFF'
            tc.variables['wxUSE_LIBNOTIFY'] = 'OFF'
            tc.variables['wxUSE_LIBMSPACK'] = 'OFF'
            tc.variables['wxUSE_LIBGNOMEVFS'] = 'OFF'

        tc.variables['wxUSE_LIBPNG'] = 'sys' if self.options.png != 'off' else 'OFF'
        tc.variables['wxUSE_LIBJPEG'] = 'sys' if self.options.jpeg != 'off' else 'OFF'
        tc.variables['wxUSE_LIBTIFF'] = 'sys' if self.options.tiff != 'off' else 'OFF'
        tc.variables['wxUSE_ZLIB'] = 'sys' if self.options.zlib != 'off' else 'OFF'
        tc.variables['wxUSE_EXPAT'] = 'sys' if self.options.expat != 'off' else 'OFF'
        tc.variables['wxUSE_REGEX'] = 'sys' if self.options.regex != 'off' else 'OFF'
        tc.variables['wxUSE_NANOSVG'] = 'sys' if self.options.svg != 'off' else 'OFF'

        # wxWidgets features
        tc.variables['wxUSE_UNICODE'] = self.options.unicode
        tc.variables['wxUSE_SECRETSTORE'] = self.options.get_safe("secretstore")

        # wxWidgets libraries
        tc.variables['wxUSE_AUI'] = self.options.aui
        tc.variables['wxUSE_OPENGL'] = self.options.opengl
        tc.variables['wxUSE_HTML'] = self.options.html
        tc.variables['wxUSE_MEDIACTRL'] = self.options.mediactrl
        tc.variables['wxUSE_PROPGRID'] = self.options.propgrid
        tc.variables['wxUSE_DEBUGREPORT'] = self.options.debugreport
        tc.variables['wxUSE_RIBBON'] = self.options.ribbon
        tc.variables['wxUSE_RICHTEXT'] = self.options.richtext
        tc.variables['wxUSE_SOCKETS'] = self.options.sockets
        tc.variables['wxUSE_STC'] = self.options.stc
        tc.variables['wxUSE_WEBVIEW'] = self.options.webview
        tc.variables['wxUSE_XML'] = self.options.xml
        tc.variables['wxUSE_XRC'] = self.options.xrc
        tc.variables['wxUSE_HELP'] = self.options.help
        tc.variables['wxUSE_WXHTML_HELP'] = self.options.html_help
        tc.variables['wxUSE_URL'] = self.options.protocol
        tc.variables['wxUSE_PROTOCOL'] = self.options.protocol
        tc.variables['wxUSE_FS_INET'] = self.options.fs_inet

        for item in str(self.options.custom_enables).split(","):
            if len(item) > 0:
                tc.variables[item] = True
        for item in str(self.options.custom_disables).split(","):
            if len(item) > 0:
                tc.variables[item] = False

        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern='licence.txt',
             src=os.path.join(self.source_folder, 'docs'),
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # copy setup.h
        copy(self, pattern='*setup.h',
             src=os.path.join(self.build_folder, 'lib'),
             dst=os.path.join(self.package_folder, 'include', 'wx'),
             keep_path=False)

        if self.settings.os == 'Windows':
            # copy wxrc.exe
            copy(self, pattern='*',
                 src=os.path.join(self.build_folder, 'bin'),
                 dst=os.path.join(self.package_folder, 'bin'),
                 keep_path=False)
        else:
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

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "wxWidgets")
        self.cpp_info.set_property("cmake_target_name", "wxWidgets::wxWidgets")
        self.cpp_info.set_property("pkg_config_name", "wxwidgets")

        _version = Version(self.version)
        version_suffix_major_minor = f'-{_version.major}.{_version.minor}'
        unicode = 'u' if self.options.unicode else ''

        # wx no longer uses a debug suffix for non-windows platforms from 3.1.3 onwards
        use_debug_suffix = False
        if self.settings.build_type == 'Debug' and self.settings.os == 'Windows':
            use_debug_suffix = True

        debug = 'd' if use_debug_suffix else ''

        if self.settings.os == 'Linux':
            prefix = 'wx_'
            toolkit = 'gtk2' if self.options.gtk == 2 else 'gtk3'
            version = ''
            suffix = version_suffix_major_minor
        elif self.settings.os == 'Macos':
            prefix = 'wx_'
            toolkit = 'osx_cocoa'
            version = ''
            suffix = version_suffix_major_minor
        elif self.settings.os == 'Windows':
            toolkit = 'msw'
            if self.settings.compiler == 'gcc':
                prefix = 'wx_'
                version = ''
                suffix = version_suffix_major_minor
            else:
                prefix = 'wx'
                version = f'{_version.major}{_version.minor}'
                suffix = ''

        def base_library_pattern(library):
            return '{prefix}base{version}{unicode}{debug}_%s{suffix}' % library

        def library_pattern(library):
            return '{prefix}{toolkit}{version}{unicode}{debug}_%s{suffix}' % library

        libs = []
        if not self.options.shared and self.version < '3.1.6':
            regex_suffix = '{debug}' if self.settings.os == "Windows" else '{suffix}'
            libs.append('wxregex{unicode}' + regex_suffix)
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
                scintilla_suffix = '{debug}' if self.settings.os == "Windows" else '{suffix}'
                libs.append('wxscintilla' + scintilla_suffix)
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
            compiler_prefix = {'Visual Studio': 'vc',
                               'msvc': 'vc',
                               'gcc': 'gcc',
                               'clang': 'clang'}.get(str(self.settings.compiler))

            arch_suffix = '_x64' if self.settings.arch == 'x86_64' else ''
            lib_suffix = '_dll' if self.options.shared else '_lib'
            libdir = f'{compiler_prefix}{arch_suffix}{lib_suffix}'
            libdir = os.path.join('lib', libdir)
            self.cpp_info.bindirs.append(libdir)
            self.cpp_info.libdirs.append(libdir)
            self.cpp_info.defines.append('__WXMSW__')
            # disable annoying auto-linking
            self.cpp_info.defines.extend(['wxNO_NET_LIB',
                                          'wxNO_XML_LIB',
                                          'wxNO_REGEX_LIB',
                                          'wxNO_ZLIB_LIB',
                                          'wxNO_JPEG_LIB',
                                          'wxNO_PNG_LIB',
                                          'wxNO_TIFF_LIB',
                                          'wxNO_ADV_LIB',
                                          'wxNO_HTML_LIB',
                                          'wxNO_GL_LIB',
                                          'wxNO_QA_LIB',
                                          'wxNO_XRC_LIB',
                                          'wxNO_AUI_LIB',
                                          'wxNO_PROPGRID_LIB',
                                          'wxNO_RIBBON_LIB',
                                          'wxNO_RICHTEXT_LIB',
                                          'wxNO_MEDIA_LIB',
                                          'wxNO_STC_LIB',
                                          'wxNO_WEBVIEW_LIB'])
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
        if self.settings.os == 'Windows':
            self.cpp_info.includedirs.append(os.path.join('include', 'msvc'))
        else:
            include_path = os.path.join("include", f"wx{version_suffix_major_minor}")
            self.cpp_info.includedirs = [include_path] + self.cpp_info.includedirs
