from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conan.tools.system import package_manager
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.60.0 <2.0 || >=2.0.6"


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
               "jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg"],
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
               "jpeg": "libjpeg",
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
               # WebKitGTK for GTK2 is not available as a system dependency on modern distros.
               # When gtk/system defaults to GTK3, turn this back on.
               "webview": False,
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
            self.options.rm_safe("fPIC")
        if self.settings.os != "Linux":
            self.options.rm_safe("secretstore")
            self.options.rm_safe("cairo")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    @property
    def _gtk_version(self):
        return f"gtk{self.dependencies['gtk'].options.version}"

    def system_requirements(self):
        apt = package_manager.Apt(self)
        packages = []
        if self.options.get_safe("secretstore"):
            packages.append("libsecret-1-dev")
        if self.options.webview:
            if self._gtk_version == "gtk2":
                packages.extend(["libsoup2.4-dev",
                                 "libwebkitgtk-dev"])
            else:
                packages.extend(["libsoup3.0-dev",
                                 "libwebkit2gtk-4.0-dev"])
        if self.options.get_safe("cairo"):
            packages.append("libcairo2-dev")
        apt.install(packages)

        yum = package_manager.Yum(self)
        packages = []
        if self.options.get_safe("secretstore"):
            packages.append("libsecret-devel")
        if self.options.webview:
                packages.extend(["libsoup3-devel",
                                 "webkit2gtk4.1-devel"])
        if self.options.get_safe("cairo"):
            packages.append("cairo-devel")
        yum.install(packages)

    def build_requirements(self):
        self.tool_requires("ninja/1.11.1")
        self.tool_requires("cmake/[>=3.17]")

    # TODO: add support for gtk non system version when it's ready for Conan 2
    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("xorg/system")
            self.requires("gtk/system")
            if self.options.get_safe("opengl", default=False):
                self.requires("opengl/system")
            self.requires("xkbcommon/1.6.0", options={"with_x11": True})
            # TODO: Does not work right now
            # if self.options.get_safe("cairo"):
            #    self.requires("cairo/1.18.0")
            if self.options.mediactrl:
                self.requires("gstreamer/1.22.3")
                self.requires("gst-plugins-base/1.19.2")
            self.requires("libcurl/[>=7.78.0 <9]")
        
        if self.options.jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.2")
        elif self.options.jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")
        
        self.requires("libpng/[>=1.6 <2]")
        self.requires("libtiff/4.6.0")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("expat/[>=2.6.2 <3]")
        self.requires("pcre2/10.42")
        self.requires("nanosvg/cci.20231025")

    def validate(self):
        if self.settings.os == "Linux":
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
                        "CMAKE_OSX_DEPLOYMENT_TARGET",
                        "CMAKE_OSX_DEPLOYMENT_TARGET_IGNORED")
        # Fix for strcpy_s (fix upstream?)
        if is_apple_os(self):
            cmake_version = "3.0"
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            f'cmake_minimum_required(VERSION {cmake_version})',
                            f'cmake_minimum_required(VERSION {cmake_version})\nadd_definitions(-D__STDC_WANT_LIB_EXT1__)')

    def generate(self):
        tc = CMakeToolchain(self)

        # generic build options
        tc.variables["wxBUILD_SHARED"] = self.options.shared
        tc.variables["wxBUILD_SAMPLES"] = "OFF"
        tc.variables["wxBUILD_TESTS"] = "OFF"
        tc.variables["wxBUILD_DEMOS"] = "OFF"
        tc.variables["wxBUILD_INSTALL"] = True
        if self.settings.compiler == "clang":
            tc.variables["wxBUILD_PRECOMP"] = "OFF"

        # platform-specific options
        if is_msvc(self):
            tc.variables["wxBUILD_USE_STATIC_RUNTIME"] = "MT" in str(self.settings.compiler.runtime)
            tc.variables["wxBUILD_MSVC_MULTIPROC"] = True
        if self.settings.os == "Linux":
            tc.variables["wxBUILD_TOOLKIT"] = self._gtk_version
            tc.variables["wxUSE_CAIRO"] = self.options.cairo
        # Disable some optional libraries that will otherwise lead to non-deterministic builds
        if self.settings.os != "Windows":
            tc.variables["wxUSE_LIBSDL"] = "OFF"
            tc.variables["wxUSE_LIBICONV"] = "OFF"
            tc.variables["wxUSE_LIBNOTIFY"] = "OFF"
            tc.variables["wxUSE_LIBMSPACK"] = "OFF"
            tc.variables["wxUSE_LIBGNOMEVFS"] = "OFF"

        tc.variables["wxUSE_LIBPNG"] = "sys"
        tc.variables["wxUSE_LIBJPEG"] = "sys"
        tc.variables["wxUSE_LIBTIFF"] = "sys"
        tc.variables["wxUSE_ZLIB"] = "sys"
        tc.variables["wxUSE_EXPAT"] = "sys"
        tc.variables["wxUSE_REGEX"] = "sys"
        tc.variables["wxUSE_NANOSVG"] = "sys"

        # wxWidgets features
        tc.variables["wxUSE_SECRETSTORE"] = self.options.get_safe("secretstore")

        # wxWidgets libraries
        tc.variables["wxUSE_AUI"] = self.options.aui
        tc.variables["wxUSE_OPENGL"] = self.options.get_safe("opengl", default=False)
        tc.variables["wxUSE_HTML"] = self.options.html
        tc.variables["wxUSE_MEDIACTRL"] = self.options.mediactrl
        tc.variables["wxUSE_PROPGRID"] = self.options.propgrid
        tc.variables["wxUSE_DEBUGREPORT"] = self.options.debugreport
        tc.variables["wxUSE_RIBBON"] = self.options.ribbon
        tc.variables["wxUSE_RICHTEXT"] = self.options.richtext
        tc.variables["wxUSE_SOCKETS"] = self.options.sockets
        tc.variables["wxUSE_STC"] = self.options.stc
        tc.variables["wxUSE_WEBVIEW"] = self.options.webview
        tc.variables["wxUSE_XML"] = self.options.xml
        tc.variables["wxUSE_XRC"] = self.options.xrc
        tc.variables["wxUSE_HELP"] = self.options.help
        tc.variables["wxUSE_WXHTML_HELP"] = self.options.html_help
        tc.variables["wxUSE_URL"] = self.options.protocol
        tc.variables["wxUSE_PROTOCOL"] = self.options.protocol
        tc.variables["wxUSE_FS_INET"] = self.options.fs_inet
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"

        for item in str(self.options.custom_enables).split(","):
            if len(item) > 0:
                tc.variables[item] = True
        for item in str(self.options.custom_disables).split(","):
            if len(item) > 0:
                tc.variables[item] = False

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("expat", "cmake_file_name", "EXPAT")
        deps.set_property("expat", "cmake_target_name", "EXPAT")
        deps.set_property("nanosvg", "cmake_file_name", "NanoSVG")
        deps.set_property("nanosvg", "cmake_target_name", "NanoSVG::nanosvg")
        deps.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="licence.txt",
             src=os.path.join(self.source_folder, "docs"),
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # remove cmake files
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # copy setup.h
        copy(self, pattern="*setup.h",
             src=os.path.join(self.build_folder, "lib"),
             dst=os.path.join(self.package_folder, "include", "wx"),
             keep_path=False)

        if self.settings.os == "Windows":
            # copy wxrc.exe
            copy(self, pattern="*",
                 src=os.path.join(self.build_folder, "bin"),
                 dst=os.path.join(self.package_folder, "bin"),
                 keep_path=False)
        else:
            # make relative symlink
            bin_dir = os.path.join(self.package_folder, "bin")
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
        version_suffix_major_minor = f"-{_version.major}.{_version.minor}"

        # wx no longer uses a debug suffix for non-windows platforms from 3.1.3 onwards
        use_debug_suffix = False
        if self.settings.build_type == "Debug" and self.settings.os == "Windows":
            use_debug_suffix = True

        debug = "d" if use_debug_suffix else ""

        if self.settings.os == "Linux":
            prefix = "wx_"
            toolkit = self._gtk_version
            version = ""
            suffix = version_suffix_major_minor
        elif self.settings.os == "Macos":
            prefix = "wx_"
            toolkit = "osx_cocoa"
            version = ""
            suffix = version_suffix_major_minor
        elif self.settings.os == "Windows":
            toolkit = "msw"
            if is_msvc(self):
                prefix = "wx"
                version = f"{_version.major}{_version.minor}"
                suffix = ""
            else:
                prefix = "wx_"
                version = ""
                suffix = version_suffix_major_minor

        def base_library_pattern(library):
            return "{prefix}base{version}u{debug}_%s{suffix}" % library

        def library_pattern(library):
            return "{prefix}{toolkit}{version}u{debug}_%s{suffix}" % library

        libs = []
        libs.append("{prefix}base{version}u{debug}{suffix}")
        libs.append(library_pattern("core"))
        libs.append(library_pattern("adv"))
        if self.options.sockets:
            libs.append(base_library_pattern("net"))
        if self.options.xml:
            libs.append(base_library_pattern("xml"))
        if self.options.aui:
            libs.append(library_pattern("aui"))
        if self.options.get_safe("opengl", default=False):
            libs.append(library_pattern("gl"))
        if self.options.html:
            libs.append(library_pattern("html"))
        if self.options.mediactrl:
            libs.append(library_pattern("media"))
        if self.options.propgrid:
            libs.append(library_pattern("propgrid"))
        if self.options.debugreport:
            libs.append(library_pattern("qa"))
        if self.options.ribbon:
            libs.append(library_pattern("ribbon"))
        if self.options.richtext:
            libs.append(library_pattern("richtext"))
        if self.options.stc:
            if not self.options.shared:
                scintilla_suffix = "{debug}" if self.settings.os == "Windows" else "{suffix}"
                libs.append("wxscintilla" + scintilla_suffix)
            libs.append(library_pattern("stc"))
        if self.options.webview:
            libs.append(library_pattern("webview"))
        if self.options.xrc:
            libs.append(library_pattern("xrc"))
        for lib in reversed(libs):
            self.cpp_info.libs.append(lib.format(prefix=prefix,
                                                 toolkit=toolkit,
                                                 version=version,
                                                 debug=debug,
                                                 suffix=suffix))

        self.cpp_info.defines.append("wxUSE_GUI=1")
        if self.settings.build_type == "Debug":
            self.cpp_info.defines.append("__WXDEBUG__")
        if self.options.shared:
            self.cpp_info.defines.append("WXUSINGDLL")
        if self.settings.os == "Linux":
            self.cpp_info.defines.append("__WXGTK__")
            self.cpp_info.system_libs.extend(["dl", "pthread", "SM"])
        elif self.settings.os == "Macos":
            self.cpp_info.defines.extend(["__WXMAC__", "__WXOSX__", "__WXOSX_COCOA__"])
            for framework in ["Carbon",
                              "Cocoa",
                              "AudioToolbox",
                              "OpenGL",
                              "AppKit",
                              "AVKit",
                              "AVFoundation",
                              "Foundation",
                              "IOKit",
                              "ApplicationServices",
                              "CoreFoundation",
                              "CoreText",
                              "CoreGraphics",
                              "CoreServices",
                              "CoreMedia",
                              "CFNetwork",
                              "Security",
                              "ImageIO",
                              "System",
                              "WebKit",
                              "QuartzCore"]:
                self.cpp_info.frameworks.append(framework)
        elif self.settings.os == "Windows":
            # see cmake/init.cmake
            compiler_prefix = {"Visual Studio": "vc",
                               "msvc": "vc",
                               "gcc": "gcc",
                               "clang": "clang"}.get(str(self.settings.compiler))

            arch_suffix = "_x64" if self.settings.arch == "x86_64" else ""
            lib_suffix = "_dll" if self.options.shared else "_lib"
            libdir = f"{compiler_prefix}{arch_suffix}{lib_suffix}"
            libdir = os.path.join("lib", libdir)
            self.cpp_info.bindirs.append(libdir)
            self.cpp_info.libdirs.append(libdir)
            self.cpp_info.defines.append("__WXMSW__")
            # disable annoying auto-linking
            self.cpp_info.defines.extend(["wxNO_NET_LIB",
                                          "wxNO_XML_LIB",
                                          "wxNO_REGEX_LIB",
                                          "wxNO_ZLIB_LIB",
                                          "wxNO_JPEG_LIB",
                                          "wxNO_PNG_LIB",
                                          "wxNO_TIFF_LIB",
                                          "wxNO_ADV_LIB",
                                          "wxNO_HTML_LIB",
                                          "wxNO_GL_LIB",
                                          "wxNO_QA_LIB",
                                          "wxNO_XRC_LIB",
                                          "wxNO_AUI_LIB",
                                          "wxNO_PROPGRID_LIB",
                                          "wxNO_RIBBON_LIB",
                                          "wxNO_RICHTEXT_LIB",
                                          "wxNO_MEDIA_LIB",
                                          "wxNO_STC_LIB",
                                          "wxNO_WEBVIEW_LIB"])
            self.cpp_info.system_libs.extend(["kernel32",
                                              "user32",
                                              "gdi32",
                                              "comdlg32",
                                              "winspool",
                                              "shell32",
                                              "comctl32",
                                              "ole32",
                                              "oleaut32",
                                              "imm32",
                                              "uuid",
                                              "wininet",
                                              "rpcrt4",
                                              "winmm",
                                              "advapi32",
                                              "msimg32",
                                              "opengl32",
                                              "ws2_32",
                                              "wsock32"])
            # Link a few libraries that are needed when using gcc on windows
            if self.settings.compiler == "gcc":
                self.cpp_info.system_libs.extend(["uxtheme",
                                                  "version",
                                                  "shlwapi",
                                                  "oleacc"])
        if is_msvc(self):
            self.cpp_info.includedirs.append(os.path.join("include", "msvc"))
        else:
            include_path = os.path.join("include", f"wx{version_suffix_major_minor}")
            self.cpp_info.includedirs = [include_path] + self.cpp_info.includedirs
