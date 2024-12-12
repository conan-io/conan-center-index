import os
from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
from conan.tools.system import package_manager

required_conan_version = ">=2.0.6"


class wxWidgetsConan(ConanFile):
    name = "wxwidgets"
    description = "wxWidgets is a C++ library that lets developers create applications for Windows, macOS, " \
                  "Linux and other platforms with a single code base."
    topics = ("wxwidgets", "gui", "ui")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.wxwidgets.org"
    license = "wxWidgets"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "toolkit": ["native", "gtk3", "gtk4", "qt5"],
        "aui": [True, False],
        "cairo": [True, False],
        "debugreport": [True, False],
        "fs_inet": [True, False],
        "glcanvas_egl": [True, False],
        "help": [True, False],
        "html": [True, False],
        "html_help": [True, False],
        "jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg"],
        "libiconv": [True, False],
        "mediactrl": [True, False],
        "opengl": [True, False],
        "private_fonts": [True, False],
        "propgrid": [True, False],
        "protocol": [True, False],
        "ribbon": [True, False],
        "richtext": [True, False],
        "secretstore": [True, False],
        "sockets": [True, False],
        "sound": [True, False],
        "stc": [True, False],
        "url": [True, False],
        "webrequest": [True, False],
        "webview": [True, False],
        "xml": [True, False],
        "xrc": [True, False],
        "custom_enables": ["ANY"],  # comma-separated list
        "custom_disables": ["ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "toolkit": "native",
        "aui": True,
        "cairo": True,
        "debugreport": True,
        "fs_inet": True,
        "glcanvas_egl": True,
        "help": True,
        "html": True,
        "html_help": True,
        "jpeg": "libjpeg",
        "libiconv": True,
        "mediactrl": False,
        "opengl": True,
        "private_fonts": True,
        "propgrid": True,
        "protocol": True,
        "ribbon": True,
        "richtext": True,
        "secretstore": True,
        "sockets": True,
        "sound": True,
        "stc": True,
        "url": True,
        "webrequest": True,
        "webview": False,
        "xml": True,
        "xrc": True,
        "custom_enables": "",
        "custom_disables": "",
    }

    @property
    def _toolkit(self):
        if self.options.toolkit == "native":
            if self.settings.os == "Windows":
                return "msw"
            if self.settings.os == "iOS":
                return "osx_iphone"
            if is_apple_os(self):
                return "osx_cocoa"
        elif self.options.toolkit == "qt5":
            return "qt"
        return self.options.toolkit.value

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        if not is_apple_os(self) and self.settings.os != "Windows":
            # GTK4 is not well-supported yet as of 2024-12 and fails with several errors. E.g.:
            # include/gtk-4.0/gdk/gdkevents.h:106:16: error: ‘struct’ tag used in naming ‘union _GdkEvent’ [-fpermissive]
            # src/common/popupcmn.cpp:384:29: error: ‘gtk_widget_get_window’ was not declared in this scope
            self.options.toolkit = "gtk3"
            # GStreamer recipe on CCI is currently broken
            self.options.mediactrl = False
        else:
            self.options.cairo = False
        if self.settings.os == "Windows":
            self.options.rm_safe("libiconv")
            self.options.rm_safe("glcanvas_egl")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.opengl or self._toolkit != "gtk3":
            self.options.rm_safe("glcanvas_egl")
        if not self._toolkit.startswith("gtk"):
            self.options.rm_safe("private_fonts")

    def requirements(self):
        if self._toolkit == "gtk3":
            # Used in gtk/private/wrapgtk.h and other public headers
            self.requires("gtk/3.24.43", transitive_headers=True, transitive_libs=True)
        elif self._toolkit == "gtk4":
            # Used in gtk/private/wrapgtk.h and other public headers
            self.requires("gtk/4.15.6", transitive_headers=True, transitive_libs=True)
        elif self._toolkit == "qt":
            # Used in wx/qt/private/converter.h and other public headers
            self.requires("qt/[~5.15]", transitive_headers=True, transitive_libs=True, run=can_run(self))

        self.requires("expat/[>=2.6.2 <3]")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("libtiff/4.6.0")
        self.requires("nanosvg/cci.20231025")
        self.requires("pcre2/10.42")
        self.requires("xz_utils/[>=5.4.5 <6]")
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.2")
        elif self.options.jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")

        if self.options.opengl:
            # Used in wx/unix/glx11.h and other public headers
            self.requires("opengl/system", transitive_headers=True, transitive_libs=True)
        if self.options.cairo and not self._toolkit.startswith("gtk"):
            self.requires("cairo/1.18.0")
        if self.options.get_safe("private_fonts"):
            self.requires("fontconfig/2.15.0")

        if self.settings.os != "Windows":
            if self.options.get_safe("glcanvas_egl"):
                self.requires("wayland/1.22.0")
            if self.options.libiconv:
                self.requires("libiconv/1.17")
            if self.options.sound:
                self.requires("sdl/2.30.9")
        if self.settings.os != "Windows" and not is_apple_os(self):
            if self.options.secretstore:
                self.requires("libsecret/0.21.4")
            if self.options.mediactrl and self._toolkit.startswith("gtk"):
                self.requires("gstreamer/1.22.3")
                self.requires("gst-plugins-base/1.19.2")
            if self._toolkit.startswith("gtk"):
                self.requires("xkbcommon/1.6.0", options={"with_x11": True})
            if self.options.webrequest:
                self.requires("libcurl/[>=7.78.0 <9]")

    def system_requirements(self):
        if self.options.webview and self._toolkit.startswith("gtk"):
            # webkit2 is also used in a gtk/private/webkit.h public header
            apt = package_manager.Apt(self)
            apt.install(["libsoup3.0-dev", "libwebkit2gtk-4.0-dev"])
            yum = package_manager.Yum(self)
            yum.install(["libsoup3-devel", "webkit2gtk4.1-devel"])

    def validate(self):
        if self.options.toolkit == "native" and not (is_apple_os(self) or self.settings.os == "Windows"):
            raise ConanInvalidConfiguration(f"A 'native' toolkit is not available on {self.settings.os}, use GTK or Qt instead")
        if self.settings.os != "Windows" and not is_apple_os(self) and self._toolkit.startswith("gtk"):
            if not self.dependencies.direct_host["xkbcommon"].options.with_x11:
                raise ConanInvalidConfiguration("The 'with_x11' option for the 'xkbcommon' package must be enabled")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.17 <4]")
        self.tool_requires("ninja/[>=1.10.2 <2]")
        if self._toolkit == "qt" and not can_run(self):
            self.tool_requires("qt/<host_version>")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
        # Don't change library names when cross-compiling
        replace_in_file(self, os.path.join(self.source_folder, "build", "cmake", "functions.cmake"),
                        'set(cross_target "-${CMAKE_SYSTEM_NAME}")',
                        'set(cross_target)')
        # Don't override Conan's toolchain
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "CMAKE_OSX_DEPLOYMENT_TARGET",
                        "CMAKE_OSX_DEPLOYMENT_TARGET_IGNORED")

    def generate(self):
        tc = CMakeToolchain(self)

        # generic build options
        tc.variables["wxBUILD_SHARED"] = self.options.shared
        tc.variables["wxBUILD_MONOLITHIC"] = True
        tc.variables["wxBUILD_SAMPLES"] = False
        tc.variables["wxBUILD_TESTS"] = False
        tc.variables["wxBUILD_DEMOS"] = False
        tc.variables["wxBUILD_INSTALL"] = True
        if self.settings.compiler == "clang":
            tc.variables["wxBUILD_PRECOMP"] = False

        tc.variables["wxBUILD_TOOLKIT"] = self._toolkit

        # platform-specific options
        if is_msvc(self):
            tc.variables["wxBUILD_USE_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
            tc.variables["wxBUILD_MSVC_MULTIPROC"] = True

        tc.variables["wxUSE_AUI"] = self.options.aui
        tc.variables["wxUSE_CAIRO"] = self.options.cairo
        tc.variables["wxUSE_DEBUGREPORT"] = self.options.debugreport
        tc.variables["wxUSE_EXPAT"] = "sys"
        tc.variables["wxUSE_FS_INET"] = self.options.fs_inet
        tc.variables["wxUSE_GLCANVAS_EGL"] = self.options.get_safe("glcanvas_egl", False)
        tc.variables["wxUSE_GTKPRINT"] = self._toolkit.startswith("gtk")
        tc.variables["wxUSE_HELP"] = self.options.help
        tc.variables["wxUSE_HTML"] = self.options.html
        tc.variables["wxUSE_LIBGNOMEVFS"] = False
        tc.variables["wxUSE_LIBICONV"] = self.options.get_safe("libiconv", False)
        tc.variables["wxUSE_LIBJPEG"] = "sys"
        tc.variables["wxUSE_LIBLZMA"] = True
        tc.variables["wxUSE_LIBMSPACK"] = False
        tc.variables["wxUSE_LIBNOTIFY"] = False
        tc.variables["wxUSE_LIBPNG"] = "sys"
        tc.variables["wxUSE_LIBSDL"] = self.options.sound
        tc.variables["wxUSE_LIBTIFF"] = "sys"
        tc.variables["wxUSE_MEDIACTRL"] = self.options.mediactrl
        tc.variables["wxUSE_NANOSVG"] = "sys"
        tc.variables["wxUSE_OPENGL"] = self.options.opengl
        tc.variables["wxUSE_PRIVATE_FONTS"] = self.options.get_safe("private_fonts", False)
        tc.variables["wxUSE_PROPGRID"] = self.options.propgrid
        tc.variables["wxUSE_PROTOCOL"] = self.options.protocol
        tc.variables["wxUSE_REGEX"] = "sys"
        tc.variables["wxUSE_RIBBON"] = self.options.ribbon
        tc.variables["wxUSE_RICHTEXT"] = self.options.richtext
        tc.variables["wxUSE_SECRETSTORE"] = self.options.secretstore
        tc.variables["wxUSE_SOCKETS"] = self.options.sockets
        tc.variables["wxUSE_SOUND"] = self.options.sound
        tc.variables["wxUSE_SPELLCHECK"] = False
        tc.variables["wxUSE_STC"] = self.options.stc
        tc.variables["wxUSE_URL"] = self.options.protocol
        tc.variables["wxUSE_WEBREQUEST"] = self.options.webrequest
        tc.variables["wxUSE_WEBVIEW"] = self.options.webview
        tc.variables["wxUSE_WXHTML_HELP"] = self.options.html_help
        tc.variables["wxUSE_XML"] = self.options.xml
        tc.variables["wxUSE_XRC"] = self.options.xrc
        tc.variables["wxUSE_ZLIB"] = "sys"

        tc.cache_variables["CMAKE_CONFIGURATION_TYPES"] = "Debug;Release;RelWithDebInfo;MinSizeRel"
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"

        for item in str(self.options.custom_enables).split(","):
            item = item.strip()
            if item:
                tc.variables[item] = True
        for item in str(self.options.custom_disables).split(","):
            item = item.strip()
            if item:
                tc.variables[item] = False

        if is_apple_os(self):
            # Fix for strcpy_s (fix upstream?)
            tc.preprocessor_definitions["__STDC_WANT_LIB_EXT1__"] = ""

        # Disable auto-detection of dependencies
        for pkg in [
            "Cairo",
            "CURL",
            "FONTCONFIG",
            "GNOMEVFS2",
            "GSPELL",
            "GSTREAMER",
            "GTKPRINT",
            "ICONV",
            "LibLZMA",
            "LIBNOTIFY",
            "LIBSECRET",
            "LIBSOUP",
            "MSPACK",
            "OpenGL",
            "PANGOFT2",
            "SDL2",
            "WAYLANDEGL",
            "WEBKIT",
            "WEBKIT2",
            "XKBCommon",
            "XTEST",
        ]:
            tc.variables[f"CMAKE_REQUIRE_FIND_PACKAGE_{pkg}"] = True

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("cairo", "cmake_file_name", "Cairo")
        deps.set_property("expat", "cmake_file_name", "EXPAT")
        deps.set_property("expat", "cmake_target_name", "EXPAT")
        deps.set_property("fontconfig", "cmake_file_name", "FONTCONFIG")
        deps.set_property("gnomevfs2", "cmake_file_name", "GNOMEVFS2")
        deps.set_property("gspell", "cmake_file_name", "GSPELL")
        deps.set_property("gstreamer", "cmake_file_name", "GSTREAMER")
        deps.set_property("iconv", "cmake_file_name", "ICONV")
        deps.set_property("libcurl", "cmake_file_name", "CURL")
        deps.set_property("libmspack", "cmake_file_name", "MSPACK")
        deps.set_property("libnotify", "cmake_file_name", "LIBNOTIFY")
        deps.set_property("libsdl", "cmake_file_name", "SDL2")
        deps.set_property("libsecret", "cmake_file_name", "LIBSECRET")
        deps.set_property("libsoup", "cmake_file_name", "LIBSOUP")
        deps.set_property("libxtst", "cmake_file_name", "XTEST")
        deps.set_property("nanosvg", "cmake_file_name", "NanoSVG")
        deps.set_property("nanosvg", "cmake_target_name", "NanoSVG::nanosvg")
        deps.set_property("webkit", "cmake_file_name", "WEBKIT2")
        if self._toolkit.startswith("gtk"):
            deps.set_property("gtk", "cmake_file_name", self._toolkit.upper())
        deps.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="licence.txt",
             src=os.path.join(self.source_folder, "docs"),
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        if self.settings.os == "Windows":
            # copy wxrc.exe
            copy(self, pattern="*",
                 src=os.path.join(self.build_folder, "bin"),
                 dst=os.path.join(self.package_folder, "bin"),
                 keep_path=False)
        else:
            # make symlinks relative
            bin_dir = Path(self.package_folder, "bin")
            for path in bin_dir.iterdir():
                if path.is_symlink() and path.readlink().is_absolute():
                    target = path.readlink()
                    if target.is_relative_to(bin_dir):
                        rel = target.relative_to(bin_dir)
                    else:
                        rel = Path("..", target.relative_to(self.package_folder))
                    path.unlink()
                    path.symlink_to(rel)

    @property
    def _api_version(self):
        version = Version(self.version)
        return f"{version.major}.{version.minor}"

    def _format_lib(self, lib=None):
        # https://github.com/wxWidgets/wxWidgets/blob/v3.2.6/build/cmake/functions.cmake#L257-L279
        lib_suffix = f"_{lib}" if lib else ""
        if is_msvc(self) and self.options.shared:
            version = Version(self.version)
            debug = "d" if self.settings.build_type == "Debug" else ""
            return f"wx{self._toolkit}{version.major}{version.minor}u{debug}{lib_suffix}"
        return f"wx_{self._toolkit}u{lib_suffix}-{self._api_version}"

    def _format_builtin_lib(self, lib):
        # https://github.com/wxWidgets/wxWidgets/blob/v3.2.6/build/cmake/functions.cmake#L557-L560
        debug = "d" if is_msvc(self) and self.settings.build_type == "Debug" else ""
        return f"wx{lib}{debug}-{self._api_version}"

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "wxWidgets")
        self.cpp_info.set_property("cmake_target_name", "wxWidgets::wxWidgets")
        self.cpp_info.set_property("pkg_config_name", "wxwidgets")

        # wxBUILD_MONOLITHIC is set, so only a single library is produced
        self.cpp_info.libs = [self._format_lib()]
        # Third-party libraries are not included in the monolith
        if not self.options.shared and self.options.stc:
            self.cpp_info.libs.append(self._format_builtin_lib("scintilla"))
            self.cpp_info.defines.append("__WX__")

        if self.settings.os == "Windows":
            # see cmake/init.cmake
            compiler_prefix = {
                "msvc": "vc",
                "gcc": "gcc",
                "clang": "clang",
            }.get(str(self.settings.compiler))
            arch_suffix = "_x64" if self.settings.arch == "x86_64" else ""
            lib_suffix = "_dll" if self.options.shared else "_lib"
            libdir = os.path.join("lib", f"{compiler_prefix}{arch_suffix}{lib_suffix}")
            self.cpp_info.bindirs.append(libdir)
            self.cpp_info.libdirs.append(libdir)

        if is_msvc(self):
            self.cpp_info.includedirs.append(os.path.join("include", "msvc"))
        else:
            self.cpp_info.includedirs.append(os.path.join("include", f"wx-{self._api_version}"))
        # e.g. lib/wx/include/gtk3-unicode-static-3.2
        lib_includedir = next(Path(self.package_folder, "lib", "wx", "include").iterdir())
        lib_includedir = lib_includedir.relative_to(self.package_folder)
        self.cpp_info.includedirs.append(lib_includedir)

        # https://github.com/wxWidgets/wxWidgets/blob/v3.2.6/build/cmake/functions.cmake
        self.cpp_info.defines.append("_UNICODE")
        if self.settings.os == "Windows":
            self.cpp_info.defines.append("UNICODE")
        if self.settings.os != "Windows":
            self.cpp_info.defines.append("-D_FILE_OFFSET_BITS=64")
        if self.options.shared:
            self.cpp_info.defines.append("WXUSINGDLL")
        # https://github.com/wxWidgets/wxWidgets/blob/v3.2.6/build/cmake/toolkit.cmake
        self.cpp_info.defines.append(f"__WX{self._toolkit.upper()}__")
        if self._toolkit.startswith("gtk"):
            self.cpp_info.defines.append("__WXGTK__")
        elif self._toolkit == "qt":
            self.cpp_info.defines.append("__WXQT__")
        if is_apple_os(self):
            self.cpp_info.defines.extend(["__WXMAC__", "__WXOSX__"])
        if self.settings.os == "Windows":
            # disable annoying auto-linking
            self.cpp_info.defines.extend([
                "wxNO_ADV_LIB",
                "wxNO_AUI_LIB",
                "wxNO_GL_LIB",
                "wxNO_HTML_LIB",
                "wxNO_JPEG_LIB",
                "wxNO_MEDIA_LIB",
                "wxNO_NET_LIB",
                "wxNO_PNG_LIB",
                "wxNO_PROPGRID_LIB",
                "wxNO_QA_LIB",
                "wxNO_REGEX_LIB",
                "wxNO_RIBBON_LIB",
                "wxNO_RICHTEXT_LIB",
                "wxNO_STC_LIB",
                "wxNO_TIFF_LIB",
                "wxNO_WEBVIEW_LIB",
                "wxNO_XML_LIB",
                "wxNO_XRC_LIB",
                "wxNO_ZLIB_LIB",
            ])

        if self.settings.os in ["Linux", "FreeBSD"]:
            # https://github.com/wxWidgets/wxWidgets/blob/v3.2.6/build/cmake/lib/base/CMakeLists.txt#L68
            self.cpp_info.system_libs.extend(["dl", "pthread"])
        elif is_apple_os(self):
            # https://github.com/wxWidgets/wxWidgets/blob/v3.2.6/build/cmake/lib/base/CMakeLists.txt#L51-L66
            # https://github.com/wxWidgets/wxWidgets/blob/v3.2.6/build/cmake/lib/core/CMakeLists.txt#L76-L90
            self.cpp_info.frameworks.append("CoreFoundation")
            if self._toolkit == "osx_cocoa":
                self.cpp_info.frameworks.extend(["Security", "Carbon", "Cocoa", "IOKit", "QuartzCore", "AudioToolbox"])
            elif self._toolkit == "osx_iphone":
                self.cpp_info.frameworks.extend(["AudioToolbox", "CoreGraphics", "CoreText", "UIKit"])
                # https://github.com/wxWidgets/wxWidgets/blob/cf2f258cbdbc32070b1a6b0a4f6fc6e0224ea30e/build/cmake/init.cmake#L452
                if self.options.opengl:
                    self.cpp_info.frameworks.extend(["OpenGLES", "QuartzCore", "GLKit"])
            # https://github.com/wxWidgets/wxWidgets/blob/v3.2.6/build/cmake/lib/media/CMakeLists.txt#L27-L29
            if self._toolkit.startswith("osx"):
                self.cpp_info.frameworks.extend(["AVFoundation", "CoreMedia", "AVKit"])
            # https://github.com/wxWidgets/wxWidgets/blob/v3.2.6/build/cmake/lib/webview/CMakeLists.txt#L45
            if self.options.webview:
                self.cpp_info.frameworks.append("WebKit")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend([
                # https://github.com/wxWidgets/wxWidgets/blob/v3.2.6/build/cmake/functions.cmake#L347-L367
                "advapi32",
                "comctl32",
                "comdlg32",
                "gdi32",
                "gdiplus",
                "kernel32",
                "msimg32",
                "ole32",
                "oleacc",
                "oleaut32",
                "rpcrt4",
                "shell32",
                "shlwapi",
                "user32",
                "uuid",
                "uxtheme",
                "version",
                "wininet",
                "winmm",
                "winspool",
                "ws2_32",
                # https://github.com/wxWidgets/wxWidgets/blob/v3.2.6/build/cmake/lib/stc/CMakeLists.txt
                "imm32",
            ])
            if self.options.webrequest:
                self.cpp_info.system_libs.append("winhttp")
