import os
import shutil
import itertools
import glob
import textwrap
import configparser
from conans import ConanFile, tools, RunEnvironment
from conans.errors import ConanInvalidConfiguration
from conans.model import Generator


class qt(Generator):
    @property
    def filename(self):
        return "qt.conf"

    @property
    def content(self):
        return """[Paths]
Prefix = %s
ArchData = bin/archdatadir
HostData = bin/archdatadir
Data = bin/datadir
Sysconf = bin/sysconfdir
LibraryExecutables = bin/archdatadir/bin
Plugins = bin/archdatadir/plugins
Imports = bin/archdatadir/imports
Qml2Imports = bin/archdatadir/qml
Translations = bin/datadir/translations
Documentation = bin/datadir/doc
Examples = bin/datadir/examples""" % self.conanfile.deps_cpp_info["qt"].rootpath.replace("\\", "/")


class QtConan(ConanFile):
    _submodules = ["qtsvg", "qtdeclarative", "qtactiveqt", "qtscript", "qtmultimedia", "qttools", "qtxmlpatterns",
    "qttranslations", "qtdoc", "qtlocation", "qtsensors", "qtconnectivity", "qtwayland",
    "qt3d", "qtimageformats", "qtgraphicaleffects", "qtquickcontrols", "qtserialbus", "qtserialport", "qtx11extras",
    "qtmacextras", "qtwinextras", "qtandroidextras", "qtwebsockets", "qtwebchannel", "qtwebengine", "qtwebview",
    "qtquickcontrols2", "qtpurchasing", "qtcharts", "qtdatavis3d", "qtvirtualkeyboard", "qtgamepad", "qtscxml",
    "qtspeech", "qtnetworkauth", "qtremoteobjects", "qtwebglplugin", "qtlottie", "qtquicktimeline", "qtquick3d"]

    generators = "pkg_config"
    name = "qt"
    description = "Qt is a cross-platform framework for graphical user interfaces."
    topics = ("conan", "qt", "ui")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.qt.io"
    license = "LGPL-3.0"
    exports = ["patches/*.diff"]
    settings = "os", "arch", "compiler", "build_type"

    library_source = {
        "not_used": "-no-",
        "qt": "-qt-",
        "system": "-system-"
    }

    library_sources = list(library_source.keys())

    options = {
        "shared": [True, False],
        "commercial": [True, False],

        "opengl": ["no", "es2", "desktop", "dynamic"],
        "with_vulkan": [True, False],
        "openssl": [True, False],
        "with_pcre2": [True, False],
        "with_glib": [True, False],
        # "with_libiconv": [True, False],  # QTBUG-84708 Qt tests failure "invalid conversion from const char** to char**"
        "with_doubleconversion": library_source,
        "with_freetype": [True, False],
        "with_fontconfig": [True, False],
        "with_icu": [True, False],
        "with_harfbuzz": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo", False],
        "with_libpng": [True, False],
        "with_sqlite3": [True, False],
        "with_mysql": [True, False],
        "with_pq": [True, False],
        "with_odbc": [True, False],
        "with_libalsa": [True, False],
        "with_mesa": [True, False],
        "with_openal": [True, False],
        "with_zstd": [True, False],
        "with_gstreamer": [True, False],

        "gui": [True, False],
        "widgets": [True, False],

        "device": "ANY",
        "cross_compile": "ANY",
        "sysroot": "ANY",
        "config": "ANY",
        "multiconfiguration": [True, False]
    }
    options.update({module: [True, False] for module in _submodules})

    no_copy_source = True
    default_options = {
        "shared": False,
        "commercial": False,
        "opengl": "desktop",
        "with_vulkan": False,
        "openssl": True,
        "with_pcre2": True,
        "with_glib": False,
        # "with_libiconv": True, # QTBUG-84708
        "with_doubleconversion": "system",
        "with_freetype": True,
        "with_fontconfig": True,
        "with_icu": True,
        "with_harfbuzz": False,
        "with_libjpeg": "libjpeg",
        "with_libpng": True,
        "with_sqlite3": True,
        "with_mysql": True,
        "with_pq": True,
        "with_odbc": True,
        "with_libalsa": False,
        "with_mesa": True,
        "with_openal": True,
        "with_zstd": True,
        "with_gstreamer": False,

        "gui": True,
        "widgets": True,

        "device": None,
        "cross_compile": None,
        "sysroot": None,
        "config": None,
        "multiconfiguration": False
    }
    default_options.update({module: False for module in _submodules})

    short_paths = True

    @property
    def original_version(self):
        if 'dssl' not in self.version:
            return self.version
        original_version = self.version.split('.')
        return '.'.join(original_version[:-1])

    def export(self):
        self.copy("qtmodules.conf")

    def build_requirements(self):
        if tools.os_info.is_windows and self.settings.compiler == "Visual Studio":
            self.build_requires("jom/1.1.3")
        if self.options.qtwebengine:
            self.build_requires("ninja/1.10.2")
            # gperf, bison, flex, python >= 2.7.5 & < 3
            if self.settings.os != "Windows":
                self.build_requires("bison/3.7.1")
                self.build_requires("gperf/3.1.dssl1")
                self.build_requires("flex/2.6.4")

            # Check if a valid python2 is available in PATH or it will failflex
            # Start by checking if python2 can be found
            python_exe = tools.which("python2")
            if not python_exe:
                # Fall back on regular python
                python_exe = tools.which("python")

            if not python_exe:
                msg = ("Python2 must be available in PATH "
                       "in order to build Qt WebEngine")
                raise ConanInvalidConfiguration(msg)

            # In any case, check its actual version for compatibility
            from six import StringIO  # Python 2 and 3 compatible
            mybuf = StringIO()
            cmd_v = "\"{}\" --version".format(python_exe)
            self.run(cmd_v, output=mybuf)
            verstr = mybuf.getvalue().strip().split("Python ")[1]
            if verstr.endswith("+"):
                verstr = verstr[:-1]
            version = tools.Version(verstr)
            # >= 2.7.5 & < 3
            v_min = "2.7.5"
            v_max = "3.0.0"
            if (version >= v_min) and (version < v_max):
                msg = ("Found valid Python 2 required for QtWebengine:"
                       " version={}, path={}".format(mybuf.getvalue(), python_exe))
                self.output.success(msg)
            else:
                msg = ("Found Python 2 in path, but with invalid version {}"
                       " (QtWebEngine requires >= {} & < "
                       "{})\nIf you have both Python 2 and 3 installed, copy the python 2 executable to"
                       "python2(.exe)".format(verstr, v_min, v_max))
                raise ConanInvalidConfiguration(msg)

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.with_icu
            del self.options.with_fontconfig
            del self.options.with_libalsa
        if self.settings.compiler == "apple-clang":
            if tools.Version(self.settings.compiler.version) < "10.0":
                raise ConanInvalidConfiguration("Old versions of apple sdk are not supported by Qt (QTBUG-76777)")
        if self.settings.compiler in ["gcc", "clang"]:
            if tools.Version(self.settings.compiler.version) < "5.0":
                raise ConanInvalidConfiguration("qt 5.15.X does not support GCC or clang before 5.0")
        if self.settings.compiler in ["gcc", "clang"] and tools.Version(self.settings.compiler.version) < "5.3":
            del self.options.with_mysql
        if self.settings.os == "Windows":
            self.options.with_mysql = False
            self.options.opengl = "dynamic"

    def configure(self):
        # if self.settings.os != "Linux":
        #         self.options.with_libiconv = False # QTBUG-84708

        if not self.options.gui:
            del self.options.opengl
            del self.options.with_vulkan
            del self.options.with_freetype
            del self.options.with_fontconfig
            del self.options.with_harfbuzz
            del self.options.with_libjpeg
            del self.options.with_libpng

        if not self.options.qtmultimedia:
            del self.options.with_libalsa
            del self.options.with_openal
            del self.options.with_gstreamer

        if self.settings.os in ("FreeBSD", "Linux"):
            if self.options.qtwebengine:
                self.options.with_fontconfig = True
        else:
            del self.options.qtx11extras

        if self.options.multiconfiguration:
            del self.settings.build_type

        config = configparser.ConfigParser()
        config.read(os.path.join(self.recipe_folder, "qtmodules.conf"))
        submodules_tree = {}
        assert config.sections()
        for s in config.sections():
            section = str(s)
            assert section.startswith("submodule ")
            assert section.count('"') == 2
            modulename = section[section.find('"') + 1: section.rfind('"')]
            status = str(config.get(section, "status"))
            if status != "obsolete" and status != "ignore":
                submodules_tree[modulename] = {"status": status,
                                "path": str(config.get(section, "path")), "depends": []}
                if config.has_option(section, "depends"):
                    submodules_tree[modulename]["depends"] = [str(i) for i in config.get(section, "depends").split()]

        for m in submodules_tree:
            assert m in ["qtbase", "qtqa", "qtrepotools"] or m in self._submodules, "module %s is not present in recipe options : (%s)" % (m, ",".join(self._submodules))

        for m in self._submodules:
            assert m in submodules_tree, "module %s is not present in qtmodules.conf : (%s)" % (m, ",".join(submodules_tree))

        def _enablemodule(mod):
            if mod != "qtbase":
                setattr(self.options, mod, True)
            for req in submodules_tree[mod]["depends"]:
                _enablemodule(req)

        for module in self._submodules:
            if self.options.get_safe(module):
                _enablemodule(module)

    def validate(self):
        if self.options.widgets and not self.options.gui:
            raise ConanInvalidConfiguration("using option qt:widgets without option qt:gui is not possible. "
                                            "You can either disable qt:widgets or enable qt:gui")

        if self.options.qtwebengine:
            if not self.options.shared:
                raise ConanInvalidConfiguration("Static builds of Qt WebEngine are not supported")

            if not (self.options.gui and self.options.qtdeclarative and self.options.qtlocation and self.options.qtwebchannel):
                raise ConanInvalidConfiguration("option qt:qtwebengine requires also qt:gui, qt:qtdeclarative, qt:qtlocation and qt:qtwebchannel")

            if tools.cross_building(self.settings, skip_x64_x86=True):
                raise ConanInvalidConfiguration("Cross compiling Qt WebEngine is not supported")

            if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
                raise ConanInvalidConfiguration("Compiling Qt WebEngine with gcc < 5 is not supported")

        if self.settings.os == "Android" and self.options.get_safe("opengl", "no") == "desktop":
            raise ConanInvalidConfiguration("OpenGL desktop is not supported on Android. Consider using OpenGL es2")

        if self.settings.os != "Windows" and self.options.get_safe("opengl", "no") == "dynamic":
            raise ConanInvalidConfiguration("Dynamic OpenGL is supported only on Windows.")

        if self.options.get_safe("with_fontconfig", False) and not self.options.get_safe("with_freetype", False):
            raise ConanInvalidConfiguration("with_fontconfig cannot be enabled if with_freetype is disabled.")

        if self.options.with_doubleconversion == "not_used" and str(self.settings.compiler.libcxx) != "libc++":
            raise ConanInvalidConfiguration("Qt without libc++ needs qt:with_doubleconversion. "
                                            "Either enable qt:with_doubleconversion or switch to libc++")

        if "MT" in self.settings.get_safe("compiler.runtime", default="") and self.options.shared:
            raise ConanInvalidConfiguration("Qt cannot be built as shared library with static runtime")

        if self.settings.compiler == "apple-clang":
            if tools.Version(self.settings.compiler.version) < "10.0":
                raise ConanInvalidConfiguration("Old versions of apple sdk are not supported by Qt (QTBUG-76777)")
        if self.settings.compiler in ["gcc", "clang"]:
            if tools.Version(self.settings.compiler.version) < "5.0":
                raise ConanInvalidConfiguration("qt 5.X.X does not support GCC or clang before 5.0")

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.openssl:
            self.requires("openssl/1.1.1d")
        if self.options.with_pcre2:
            self.requires("pcre2/10.33")
        if self.options.get_safe("with_vulkan"):
            self.requires("vulkan-loader/1.2.172")

        if self.options.with_glib:
            self.requires("glib/2.64.0")
        # if self.options.with_libiconv: # QTBUG-84708
        #     self.requires("libiconv/1.16")# QTBUG-84708
        if self.options.with_doubleconversion == 'system' and not self.options.multiconfiguration:
            self.requires("double-conversion/3.1.5")
        if self.options.get_safe("with_freetype", False) and not self.options.multiconfiguration:
            self.requires("freetype/2.10.1")
        if self.options.get_safe("with_fontconfig", False):
            self.requires("fontconfig/2.13.91")
        if self.options.get_safe("with_icu", False):
            self.requires("icu/64.2")
        if self.options.get_safe("with_harfbuzz", False) and not self.options.multiconfiguration:
            self.requires("harfbuzz/2.6.4")
        if self.options.get_safe("with_libjpeg", False) and not self.options.multiconfiguration:
            if self.options.with_libjpeg == "libjpeg-turbo":
                self.requires("libjpeg-turbo/2.1.0")
            else:
                self.requires("libjpeg/9d")
        if self.options.get_safe("with_libpng", False) and not self.options.multiconfiguration:
            self.requires("libpng/1.6.37")
        if self.options.with_sqlite3 and not self.options.multiconfiguration:
            self.requires("sqlite3/3.31.0")
            self.options["sqlite3"].enable_column_metadata = True
        if self.options.get_safe("with_mysql", False):
            self.requires("libmysqlclient/8.0.17")
        if self.options.with_pq:
            self.requires("libpq/11.5")
        if self.options.with_odbc:
            if self.settings.os != "Windows":
                self.requires("odbc/2.3.7")
        if self.options.get_safe("with_openal", False):
            self.requires("openal/1.20.1")
        if self.options.get_safe("with_libalsa", False):
            self.requires("libalsa/1.1.9")
        if self.options.gui and self.settings.os == "Linux":
            if not tools.cross_building(self, skip_x64_x86=True):
                self.requires("xkbcommon/1.3.0")
        if self.options.opengl in ["desktop", "es2"]:
            if self.settings.os == 'Linux' and self.options.with_mesa:
                self.requires('mesa/19.3.1')
        if self.options.with_zstd:
            self.requires("zstd/1.5.0")
        if self.options.qtwebengine and self.settings.os == "Linux":
            self.requires("expat/2.4.1")
            self.requires("opus/1.3.1")
        if self.options.get_safe("with_gstreamer", False):
            raise ConanInvalidConfiguration("gst-plugins-base is not yet available on Conan-Center-Index, please use option with_gstreamer=False")
            self.requires("gst-plugins-base/1.19.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.original_version])
        shutil.move("qt-everywhere-src-%s" % self.original_version, "qt5")

        for patch in self.conan_data.get("patches", {}).get(self.original_version, []):
            tools.patch(**patch)
        for f in ["renderer", os.path.join("renderer", "core"), os.path.join("renderer", "platform")]:
            tools.replace_in_file(os.path.join(self.source_folder, "qt5", "qtwebengine", "src", "3rdparty", "chromium", "third_party", "blink", f, "BUILD.gn"),
                                  "  if (enable_precompiled_headers) {\n    if (is_win) {",
                                  "  if (enable_precompiled_headers) {\n    if (false) {"
                                  )

    def _make_program(self):
        if self.settings.compiler == "Visual Studio":
            return "jom"
        elif tools.os_info.is_windows:
            return "mingw32-make"
        else:
            return "make"

    def _xplatform(self):
        if self.settings.os == "Linux":
            if self.settings.compiler == "gcc":
                return {"x86": "linux-g++-32",
                        "armv6": "linux-arm-gnueabi-g++",
                        "armv7": "linux-arm-gnueabi-g++",
                        "armv7hf": "linux-arm-gnueabi-g++",
                        "armv8": "linux-aarch64-gnu-g++"}.get(str(self.settings.arch), "linux-g++")
            elif self.settings.compiler == "clang":
                if self.settings.arch == "x86":
                    return "linux-clang-libc++-32" if self.settings.compiler.libcxx == "libc++" else "linux-clang-32"
                elif self.settings.arch == "x86_64":
                    return "linux-clang-libc++" if self.settings.compiler.libcxx == "libc++" else "linux-clang"

        elif self.settings.os == "Macos":
            return {"clang": "macx-clang",
                    "apple-clang": "macx-clang",
                    "gcc": "macx-g++"}.get(str(self.settings.compiler))

        elif self.settings.os == "iOS":
            if self.settings.compiler == "apple-clang":
                return "macx-ios-clang"

        elif self.settings.os == "watchOS":
            if self.settings.compiler == "apple-clang":
                return "macx-watchos-clang"

        elif self.settings.os == "tvOS":
            if self.settings.compiler == "apple-clang":
                return "macx-tvos-clang"

        elif self.settings.os == "Android":
            if self.settings.compiler == "clang":
                return "android-clang"

        elif self.settings.os == "Windows":
            return {"Visual Studio": "win32-msvc",
                    "gcc": "win32-g++",
                    "clang": "win32-clang-g++"}.get(str(self.settings.compiler))

        elif self.settings.os == "WindowsStore":
            if self.settings.compiler == "Visual Studio":
                return {"14": {"armv7": "winrt-arm-msvc2015",
                               "x86": "winrt-x86-msvc2015",
                               "x86_64": "winrt-x64-msvc2015"},
                        "15": {"armv7": "winrt-arm-msvc2017",
                               "x86": "winrt-x86-msvc2017",
                               "x86_64": "winrt-x64-msvc2017"},
                        "16": {"armv7": "winrt-arm-msvc2019",
                               "x86": "winrt-x86-msvc2019",
                               "x86_64": "winrt-x64-msvc2019"}
                        }.get(str(self.settings.compiler.version)).get(str(self.settings.arch))

        elif self.settings.os == "FreeBSD":
            return {"clang": "freebsd-clang",
                    "gcc": "freebsd-g++"}.get(str(self.settings.compiler))

        elif self.settings.os == "SunOS":
            if self.settings.compiler == "sun-cc":
                if self.settings.arch == "sparc":
                    return "solaris-cc-stlport" if self.settings.compiler.libcxx == "libstlport" else "solaris-cc"
                elif self.settings.arch == "sparcv9":
                    return "solaris-cc64-stlport" if self.settings.compiler.libcxx == "libstlport" else "solaris-cc64"
            elif self.settings.compiler == "gcc":
                return {"sparc": "solaris-g++",
                        "sparcv9": "solaris-g++-64"}.get(str(self.settings.arch))
        elif self.settings.os == "Neutrino" and self.settings.compiler == "qcc":
            return {"armv8": "qnx-aarch64le-qcc",
                    "armv8.3": "qnx-aarch64le-qcc",
                    "armv7": "qnx-armle-v7-qcc",
                    "armv7hf": "qnx-armle-v7-qcc",
                    "armv7s": "qnx-armle-v7-qcc",
                    "armv7k": "qnx-armle-v7-qcc",
                    "x86": "qnx-x86-qcc",
                    "x86_64": "qnx-x86-64-qcc"}.get(str(self.settings.arch))
        elif self.settings.os == "Emscripten" and self.settings.arch == "wasm":
            return "wasm-emscripten"

        return None

    def build(self):
        args = ["-confirm-license", "-silent", "-nomake examples", "-nomake tests",
                "-prefix %s" % self.package_folder]
        args.append("-v")
        args.append("-archdatadir  %s" % os.path.join(self.package_folder, "bin", "archdatadir"))
        args.append("-datadir  %s" % os.path.join(self.package_folder, "bin", "datadir"))
        args.append("-sysconfdir  %s" % os.path.join(self.package_folder, "bin", "sysconfdir"))
        if self.options.commercial:
            args.append("-commercial")
        else:
            args.append("-opensource")
        if not self.options.gui:
            args.append("-no-gui")
        if not self.options.widgets:
            args.append("-no-widgets")
        if not self.options.shared:
            args.insert(0, "-static")
            if self.settings.compiler == "Visual Studio":
                if self.settings.compiler.runtime == "MT" or self.settings.compiler.runtime == "MTd":
                    args.append("-static-runtime")
        else:
            args.insert(0, "-shared")
        if self.options.multiconfiguration:
            args.append("-debug-and-release")
        elif self.settings.build_type == "Debug":
            args.append("-debug")
        elif self.settings.build_type == "Release":
            args.append("-release")
        elif self.settings.build_type == "RelWithDebInfo":
            args.append("-release")
            args.append("-force-debug-info")
        elif self.settings.build_type == "MinSizeRel":
            args.append("-release")
            args.append("-optimize-size")

        for module in self._submodules:
            if not self.options.get_safe(module):
                args.append("-skip " + module)

        args.append("--zlib=system")

        # openGL
        opengl = self.options.get_safe("opengl", "no")
        if opengl == "no":
            args += ["-no-opengl"]
        elif opengl == "es2":
            args += ["-opengl es2"]
        elif opengl == "desktop":
            args += ["-opengl desktop"]
        elif opengl == "dynamic":
            args += ["-opengl dynamic"]

        if self.options.get_safe("with_vulkan", False):
            args.append("-vulkan")
        else:
            args.append("-no-vulkan")

        # openSSL
        if not self.options.openssl:
            args += ["-no-openssl"]
        else:
            if self.options["openssl"].shared:
                args += ["-openssl-runtime"]
            else:
                args += ["-openssl-linked"]

        # args.append("--iconv=" + ("gnu" if self.options.with_libiconv else "no"))# QTBUG-84708

        args.append("--glib=" + ("yes" if self.options.with_glib else "no"))
        args.append("--pcre=" + ("system" if self.options.with_pcre2 else "qt"))
        args.append("--fontconfig=" + ("yes" if self.options.get_safe("with_fontconfig", False) else "no"))
        args.append("--icu=" + ("yes" if self.options.get_safe("with_icu", False) else "no"))
        args.append("--sql-mysql=" + ("yes" if self.options.get_safe("with_mysql", False) else "no"))
        args.append("--sql-psql=" + ("yes" if self.options.with_pq else "no"))
        args.append("--sql-odbc=" + ("yes" if self.options.with_odbc else "no"))
        args.append("--zstd=" + ("yes" if self.options.with_zstd else "no"))

        if self.options.qtmultimedia:
            args.append("--alsa=" + ("yes" if self.options.get_safe("with_libalsa", False) else "no"))
            args.append("--gstreamer" if self.options.with_gstreamer else "--no-gstreamer")

        for opt, conf_arg in [
                              ("with_doubleconversion", "doubleconversion"),
                              ("with_freetype", "freetype"),
                              ("with_harfbuzz", "harfbuzz"),
                              ("with_libjpeg", "libjpeg"),
                              ("with_libpng", "libpng"),
                              ("with_sqlite3", "sqlite")]:
            value = self.options.get_safe(opt, False)
            if str(value) in self.library_sources and value:
                args += [self.library_source[str(value)] + conf_arg]
            elif value:
                if self.options.multiconfiguration:
                    args += ["-qt-" + conf_arg]
                else:
                    args += ["-system-" + conf_arg]
            else:
                args += ["-no-" + conf_arg]

        libmap = [("zlib", "ZLIB"),
                  ("openssl", "OPENSSL"),
                  ("pcre2", "PCRE2"),
                  ("glib", "GLIB"),
                  # ("libiconv", "ICONV"),# QTBUG-84708
                  ("double-conversion", "DOUBLECONVERSION"),
                  ("freetype", "FREETYPE"),
                  ("fontconfig", "FONTCONFIG"),
                  ("icu", "ICU"),
                  ("harfbuzz", "HARFBUZZ"),
                  ("libjpeg", "LIBJPEG"),
                  ("libjpeg-turbo", "LIBJPEG"),
                  ("libpng", "LIBPNG"),
                  ("sqlite3", "SQLITE"),
                  ("libmysqlclient", "MYSQL"),
                  ("libpq", "PSQL"),
                  ("odbc", "ODBC"),
                  ("sdl2", "SDL2"),
                  ("openal", "OPENAL"),
                  ("zstd", "ZSTD"),
                  ("libalsa", "ALSA"),
                  ("xkbcommon", "XKBCOMMON")]
        for package, var in libmap:
            if package in self.deps_cpp_info.deps:
                if package == "freetype":
                    args.append("\"%s_INCDIR=%s\"" % (var, self.deps_cpp_info[package].include_paths[-1]))

                args.append("\"%s_LIBS=%s\"" % (var, " ".join(self._gather_libs(package))))

        for package in self.deps_cpp_info.deps:
            args += ["-I \"%s\"" % s for s in self.deps_cpp_info[package].include_paths]
            args += ["-D %s" % s for s in self.deps_cpp_info[package].defines]
        lib_arg = "/LIBPATH:" if self.settings.compiler == "Visual Studio" else "-L"
        args.append("QMAKE_LFLAGS+=\"%s\"" % " ".join("%s%s" % (lib_arg, l) for package in self.deps_cpp_info.deps for l in self.deps_cpp_info[package].lib_paths))

        if "libmysqlclient" in self.deps_cpp_info.deps:
            args.append("-mysql_config \"%s\"" % os.path.join(self.deps_cpp_info["libmysqlclient"].rootpath, "bin", "mysql_config"))
        if "libpq" in self.deps_cpp_info.deps:
            args.append("-psql_config \"%s\"" % os.path.join(self.deps_cpp_info["libpq"].rootpath, "bin", "pg_config"))
        if self.settings.os == "Macos":
            args += ["-no-framework"]
        elif self.settings.os == "Android":
            args += ["-android-ndk-platform android-%s" % self.settings.os.api_level]
            args += ["-android-abis %s" % {"armv7": "armeabi-v7a",
                                           "armv8": "arm64-v8a",
                                           "x86": "x86",
                                           "x86_64": "x86_64"}.get(str(self.settings.arch))]

        if self.settings.get_safe("compiler.libcxx") == "libstdc++":
            args += ["-D_GLIBCXX_USE_CXX11_ABI=0"]
        elif self.settings.get_safe("compiler.libcxx") == "libstdc++11":
            args += ["-D_GLIBCXX_USE_CXX11_ABI=1"]

        if self.options.sysroot:
            args += ["-sysroot %s" % self.options.sysroot]

        if self.options.device:
            args += ["-device %s" % self.options.device]
        else:
            xplatform_val = self._xplatform()
            if xplatform_val:
                if not tools.cross_building(self.settings, skip_x64_x86=True):
                    args += ["-platform %s" % xplatform_val]
                else:
                    args += ["-xplatform %s" % xplatform_val]
            else:
                self.output.warn("host not supported: %s %s %s %s" %
                                 (self.settings.os, self.settings.compiler,
                                  self.settings.compiler.version, self.settings.arch))
        if self.options.cross_compile:
            args += ["-device-option CROSS_COMPILE=%s" % self.options.cross_compile]

        if not tools.os_info.is_windows:
            def _getenvpath(var):
                val = os.getenv(var)
                if val and tools.os_info.is_windows:
                    val = val.replace("\\", "/")
                    os.environ[var] = val
                return val
            value = _getenvpath("CC")
            if value:
                args += ['QMAKE_CC="' + value + '"',
                         'QMAKE_LINK_C="' + value + '"',
                         'QMAKE_LINK_C_SHLIB="' + value + '"']

            value = _getenvpath('CXX')
            if value:
                args += ['QMAKE_CXX="' + value + '"',
                         'QMAKE_LINK="' + value + '"',
                         'QMAKE_LINK_SHLIB="' + value + '"']

        if tools.os_info.is_linux and self.settings.compiler == "clang":
            args += ['QMAKE_CXXFLAGS+="-ftemplate-depth=1024"']

        if self.options.qtwebengine and self.settings.os == "Linux":
            args += ["-qt-webengine-ffmpeg",
                     "-system-webengine-opus"]

        if self.options.config:
            args.append(str(self.options.config))

        os.mkdir("build_folder")
        with tools.chdir("build_folder"):
            with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
                build_env = {"MAKEFLAGS": "j%d" % tools.cpu_count(), "PKG_CONFIG_PATH": [self.build_folder]}
                if self.settings.os == "Windows":
                    build_env["PATH"] = [os.path.join(self.source_folder, "qt5", "gnuwin32", "bin")]

                with tools.environment_append(build_env):

                    if tools.os_info.is_macos:
                        open(".qmake.stash" , "w").close()
                        open(".qmake.super" , "w").close()

                    self.run("%s/qt5/configure %s" % (self.source_folder, " ".join(args)), run_environment=True)
                    if tools.os_info.is_macos:
                        with open("bash_env", "w") as f:
                            f.write('export DYLD_LIBRARY_PATH="%s"' % ":".join(RunEnvironment(self).vars["DYLD_LIBRARY_PATH"]))
                    with tools.environment_append({
                        "BASH_ENV": os.path.abspath("bash_env")
                    }) if tools.os_info.is_macos else tools.no_op():
                        self.run(self._make_program(), run_environment=True)

    def _folder_to_module(self, module):
        return os.path.join("lib", "cmake", "Qt5{0}".format(module))

    def _create_folder_if_not_exists(self, path):
        if not os.path.exists(path):
            tools.mkdir(path)

    @property
    def _cmake_executables_file(self):
        return os.path.join("lib", "cmake", "Qt5Core", "conan_qt_executables_variables.cmake")

    def _cmake_qt5_private_file(self, module):
        return os.path.join(self._folder_to_module(module), "conan_qt_qt5_{0}private.cmake".format(module.lower()))

    def _cmake_qt5_variables_file(self, module):
        return os.path.join(self._folder_to_module(module), "conan_qt_qt5_{0}_variables.cmake".format(module.lower()))

    def _cmake_qt5_extra_variables_file(self, module):
        return os.path.join(self._folder_to_module(module), "conan_qt_qt5_{0}_extra_variables.cmake".format(module.lower()))

    def package(self):
        with tools.chdir("build_folder"):
            self.run("%s install" % self._make_program())
        with open(os.path.join(self.package_folder, "bin", "qt.conf"), "w") as f:
            f.write("""[Paths]
Prefix = ..
ArchData = bin/archdatadir
HostData = bin/archdatadir
Data = bin/datadir
Sysconf = bin/sysconfdir
LibraryExecutables = bin/archdatadir/bin
Plugins = bin/archdatadir/plugins
Imports = bin/archdatadir/imports
Qml2Imports = bin/archdatadir/qml
Translations = bin/datadir/translations
Documentation = bin/datadir/doc
Examples = bin/datadir/examples""")
        self.copy("*LICENSE*", src="qt5/", dst="licenses")
        for module in self._submodules:
            if not self.options.get_safe(module):
                tools.rmdir(os.path.join(self.package_folder, "licenses", module))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for mask in ["Find*.cmake", "*Config.cmake", "*-config.cmake"]:
            tools.remove_files_by_mask(self.package_folder, mask)
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la*")
        if self.settings.build_type == "Debug":
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")
        # "Qt5Bootstrap" is internal Qt library - removing it to avoid linking error, since it contains
        # symbols that are also in "Qt5Core.lib". It looks like there is no "Qt5Bootstrap.dll".
        for fl in glob.glob(os.path.join(self.package_folder, "lib", "*Qt5Bootstrap*")):
            os.remove(fl)

        for m in os.listdir(os.path.join(self.package_folder, "lib", "cmake")):
            module = os.path.join(self.package_folder, "lib", "cmake", m, "%sMacros.cmake" % m)
            if not os.path.isfile(module):
                tools.rmdir(os.path.join(self.package_folder, "lib", "cmake", m))

        extension = ""
        if self.settings.os == "Windows":
            extension = ".exe"
        v = tools.Version(self.original_version)
        filecontents = textwrap.dedent("""\
            set(QT_CMAKE_EXPORT_NAMESPACE Qt5)
            set(QT_VERSION_MAJOR {major})
            set(QT_VERSION_MINOR {minor})
            set(QT_VERSION_PATCH {patch})
        """.format(major=v.major, minor=v.minor, patch=v.patch))
        targets = {}
        targets["Core"] = ["moc", "rcc", "qmake"]
        targets["DBus"] = ["qdbuscpp2xml", "qdbusxml2cpp"]
        if self.options.widgets:
            targets["Widgets"] = ["uic"]
        if self.options.qttools:
            targets["Tools"] = ["qhelpgenerator", "qcollectiongenerator", "qdoc", "qtattributionsscanner"]
            targets[""] = ["lconvert", "lrelease", "lupdate"]
        if self.options.qtremoteobjects:
            targets["RemoteObjects"] = ["repc"]
        if self.options.qtscxml:
            targets["Scxml"] = ["qscxmlc"]
        for namespace, targets in targets.items():
            for target in targets:
                filecontents += textwrap.dedent("""\
                    if(NOT TARGET ${{QT_CMAKE_EXPORT_NAMESPACE}}::{target})
                        add_executable(${{QT_CMAKE_EXPORT_NAMESPACE}}::{target} IMPORTED)
                        set_target_properties(${{QT_CMAKE_EXPORT_NAMESPACE}}::{target} PROPERTIES IMPORTED_LOCATION ${{CMAKE_CURRENT_LIST_DIR}}/../../../bin/{target}{ext})
                        set(Qt5{namespace}_{uppercase_target}_EXECUTABLE ${{QT_CMAKE_EXPORT_NAMESPACE}}::{target})
                    endif()
                    """.format(target=target, ext=extension, namespace=namespace, uppercase_target=target.upper()))

        tools.save(os.path.join(self.package_folder, self._cmake_executables_file), filecontents)

        def _create_private_module(module, dependencies=[]):
            dependencies_string = ';'.join('Qt5::%s' % dependency for dependency in dependencies)
            contents = textwrap.dedent("""\
            if(NOT TARGET Qt5::{0}Private)
                add_library(Qt5::{0}Private INTERFACE IMPORTED)
                set_target_properties(Qt5::{0}Private PROPERTIES
                    INTERFACE_INCLUDE_DIRECTORIES "${{CMAKE_CURRENT_LIST_DIR}}/../../../include/Qt{0}/{1};${{CMAKE_CURRENT_LIST_DIR}}/../../../include/Qt{0}/{1}/Qt{0}"
                    INTERFACE_LINK_LIBRARIES "{2}"
                )

                add_library(Qt::{0}Private INTERFACE IMPORTED)
                set_target_properties(Qt::{0}Private PROPERTIES
                    INTERFACE_LINK_LIBRARIES "Qt5::{0}Private"
                    _qt_is_versionless_target "TRUE"
                )
            endif()""".format(module, self.original_version, dependencies_string))

            self._create_folder_if_not_exists(module)
            tools.save(os.path.join(self.package_folder, self._cmake_qt5_private_file(module)), contents)

        def _create_module_variables(module, deps=[], extra_vars={}):
            private_headers_dirs = [
                f"${{CMAKE_CURRENT_LIST_DIR}}/../../../include",
                f"${{CMAKE_CURRENT_LIST_DIR}}/../../../include/Qt{module}",
                f"${{CMAKE_CURRENT_LIST_DIR}}/../../../include/Qt{module}/{self.original_version}",
                f"${{CMAKE_CURRENT_LIST_DIR}}/../../../include/Qt{module}/{self.original_version}/Qt{module}"
            ]
            for dep in deps:
                private_headers_dirs.append(f"${{CMAKE_CURRENT_LIST_DIR}}/../../../include/Qt{dep}")
                private_headers_dirs.append(f"${{CMAKE_CURRENT_LIST_DIR}}/../../../include/Qt{dep}/{self.original_version}")
                private_headers_dirs.append(f"${{CMAKE_CURRENT_LIST_DIR}}/../../../include/Qt{dep}/{self.original_version}/Qt{dep}")
                if dep == 'Core':
                    private_headers_dirs.append(f"${{CMAKE_CURRENT_LIST_DIR}}/../../../bin/archdatadir/mkspecs{self._xplatform()}")

            private_headers_dirs_str = ';'.join(list(set(private_headers_dirs)))
            contents = textwrap.dedent("""\
            set(Qt5{0}_FOUND TRUE)
            set(Qt5{0}_PRIVATE_INCLUDE_DIRS "{2}")
            set(Qt5{0}_LIBRARIES Qt5::{0})
            """.format(module, self.original_version, private_headers_dirs_str))

            for key, val in extra_vars.items():
                contents += f"set({key} {val})\n"

            self._create_folder_if_not_exists(module)
            tools.save(os.path.join(self.package_folder, self._cmake_qt5_variables_file(module)), contents)

        _create_private_module("Core", ["Core"])
        _create_module_variables("Core", extra_vars=dict(Qt5_ORIGINAL_VERSION=self.original_version))

        if self.options.gui:
            extra_vars=dict()
            if self.options.get_safe("opengl", "no") in ['desktop', 'dynamic']:
                extra_vars['Qt5Gui_OPENGL_IMPLEMENTATION'] = 'GL'
            _create_module_variables("Gui", deps=['Core'], extra_vars=extra_vars)
            _create_private_module("Gui", ["CorePrivate", "Gui"])

        if self.options.qtdeclarative:
            _create_private_module("Qml", ["CorePrivate", "Qml"])
            _create_module_variables("Qml", deps=['Core'])
            _create_module_variables("QmlModels")
            if self.options.gui:
                _create_module_variables("Quick")
                if self.options.widgets:
                    _create_module_variables("QuickWidgets")
                _create_module_variables("QuickShapes")
            _create_module_variables("QmlWorkerScript")
            _create_module_variables("QuickTest")

        _create_module_variables("DBus")
        _create_module_variables("Concurrent")
        _create_module_variables("Sql")
        _create_module_variables("Network")
        _create_module_variables("Xml")
        _create_module_variables("Test")

        if self.options.widgets:
           _create_module_variables("Widgets")
        if self.options.gui and self.options.widgets:
            _create_module_variables("PrintSupport")
        if self.options.get_safe("opengl", "no") != "no" and self.options.gui:
            _create_module_variables("OpenGL")
        if self.options.widgets and self.options.get_safe("opengl", "no") != "no":
            _create_module_variables("OpenGLExtensions")

        if self.options.qttools and self.options.gui and self.options.widgets:
            _create_module_variables("UiPlugin")
            _create_module_variables("UiTools")
            _create_module_variables("Designer")
            _create_module_variables("Help")

        if self.options.qtquick3d and self.options.gui:
            _create_module_variables("Quick3DUtils")
            _create_module_variables("Quick3DAssetImport")
            _create_module_variables("Quick3DRuntimeRender")
            _create_module_variables("Quick3D")

        if self.options.qtquickcontrols2 and self.options.gui:
            _create_module_variables("QuickControls2")
            _create_module_variables("QuickTemplates2")

        if self.options.qtsvg and self.options.gui:
            _create_module_variables("Svg")

        if self.options.qtwayland and self.options.gui:
            _create_module_variables("WaylandClient")
            _create_module_variables("WaylandCompositor")

        if self.options.qtlocation:
            _create_module_variables("Positioning")
            _create_module_variables("Location")

        if self.options.qtwebchannel:
            _create_module_variables("WebChannel")

        if self.options.qtwebengine:
            _create_module_variables("WebEngineCore")
            _create_module_variables("WebEngine")
            _create_module_variables("WebEngineWidgets")

        if self.options.qtserialport:
            _create_module_variables("SerialPort")

        if self.options.qtserialbus:
            _create_module_variables("SerialBus")

        if self.options.qtsensors:
            _create_module_variables("Sensors")

        if self.options.qtscxml:
            _create_module_variables("Scxml")

        if self.options.qtpurchasing:
            _create_module_variables("Purchasing")

        if self.options.qtcharts:
            _create_module_variables("Charts")

        if self.options.qt3d:
            _create_module_variables("3DCore")
            _create_module_variables("3DRender")
            _create_module_variables("3DAnimation")
            _create_module_variables("3DInput")
            _create_module_variables("3DLogic")
            _create_module_variables("3DExtras")
            _create_module_variables("3DQuick")
            _create_module_variables("3DQuickAnimation")
            _create_module_variables("3DQuickExtras")
            _create_module_variables("3DQuickInput")
            _create_module_variables("3DQuickRender")
            _create_module_variables("3DQuickScene2D")

        if self.options.qtgamepad:
            _create_module_variables("Gamepad")

        if self.options.qtmultimedia:
            _create_module_variables("Multimedia")
            _create_module_variables("MultimediaWidgets")
            if self.options.qtdeclarative and self.options.gui:
                _create_module_variables("MultimediaQuick")
            if self.options.with_gstreamer:
                _create_module_variables("MultimediaGstTools")

        if self.options.qtwebsockets:
            _create_module_variables("WebSockets")

        if self.options.qtconnectivity:
            _create_module_variables("Bluetooth")
            _create_module_variables("Nfc")

        if self.options.qtdatavis3d:
            _create_module_variables("DataVisualization")

        if self.options.qtnetworkauth:
            _create_module_variables("NetworkAuth")

        if self.options.get_safe("qtx11extras"):
            _create_module_variables("X11Extras")

        if self.options.qtremoteobjects:
            _create_module_variables("RemoteObjects")

        if self.options.qtwinextras:
            _create_module_variables("WinExtras")

    def package_id(self):
        del self.info.options.cross_compile
        del self.info.options.sysroot
        if self.options.multiconfiguration and self.settings.compiler == "Visual Studio":
            if "MD" in self.settings.compiler.runtime:
                self.info.settings.compiler.runtime = "MD/MDd"
            else:
                self.info.settings.compiler.runtime = "MT/MTd"

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Qt5"
        self.cpp_info.names["cmake_find_package_multi"] = "Qt5"
        self.user_info._extra_cmake_variables_ = dict(Qt5_ORIGINAL_VERSION=self.original_version)
        self.user_info._extra_cmake_paths_ = {}

        libsuffix = ""
        if self.settings.build_type == "Debug":
            if self.settings.os == "Windows":
                libsuffix = "d"
            elif tools.is_apple_os(self.settings.os):
                libsuffix = "_debug"

        def _get_corrected_reqs(requires):
            reqs = []
            for r in requires:
                reqs.append(r if "::" in r else "qt%s" % r)
            return reqs

        def _create_module(module, requires=[]):
            def _make_public_include_dirs(module_name):
                return [
                    os.path.join('include'),
                    os.path.join('include', f'Qt{module_name}'),
                ]

            componentname = "qt%s" % module
            assert componentname not in self.cpp_info.components, "Module %s already present in self.cpp_info.components" % module
            self.cpp_info.components[componentname].names["cmake_find_package"] = module
            self.cpp_info.components[componentname].names["cmake_find_package_multi"] = module
            self.cpp_info.components[componentname].libs = ["Qt5%s%s" % (module, libsuffix)]
            self.cpp_info.components[componentname].includedirs = _make_public_include_dirs(module)
            self.cpp_info.components[componentname].defines = ["QT_%s_LIB" % module.upper()]
            if module != "Core" and "Core" not in requires:
                requires.append("Core")
            self.cpp_info.components[componentname].requires = _get_corrected_reqs(requires)

            if module == "Core":
                self.cpp_info.components[componentname].includedirs.append(os.path.join("bin", "archdatadir", "mkspecs", self._xplatform()))

            self.cpp_info.components[componentname].build_modules["cmake_find_package"].append(self._cmake_qt5_variables_file(module))
            self.cpp_info.components[componentname].build_modules["cmake_find_package_multi"].append(self._cmake_qt5_variables_file(module))

            if self.settings.build_type == "Release":
               self.cpp_info.components[componentname].defines.append("QT_NO_DEBUG")


        def _create_plugin(pluginname, libname, type, requires):
            componentname = "qt%s" % pluginname
            assert componentname not in self.cpp_info.components, "Plugin %s already present in self.cpp_info.components" % pluginname
            self.cpp_info.components[componentname].names["cmake_find_package"] = pluginname
            self.cpp_info.components[componentname].names["cmake_find_package_multi"] = pluginname
            if not self.options.shared:
                self.cpp_info.components[componentname].libs = [libname + libsuffix]
            self.cpp_info.components[componentname].libdirs = [os.path.join("bin", "archdatadir", "plugins", type)]
            self.cpp_info.components[componentname].includedirs = []
            if "Core" not in requires:
                requires.append("Core")
            self.cpp_info.components[componentname].requires = _get_corrected_reqs(requires)

        core_reqs = ["zlib::zlib"]
        if self.options.with_pcre2:
            core_reqs.append("pcre2::pcre2")
        if self.options.with_doubleconversion == 'system' and not self.options.multiconfiguration:
            core_reqs.append("double-conversion::double-conversion")
        if self.options.get_safe("with_icu", False):
            core_reqs.append("icu::icu")
        if self.options.with_zstd:
            core_reqs.append("zstd::zstd")
        if self.options.with_glib:
            core_reqs.append("glib::glib-2.0")

        _create_module("Core", core_reqs)
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.components["qtCore"].exelinkflags.append("-ENTRY:mainCRTStartup")

        if self.options.gui:
            gui_reqs = ["DBus"]
            if self.options.with_freetype:
                gui_reqs.append("freetype::freetype")
            if self.options.with_libpng:
                gui_reqs.append("libpng::libpng")
            if self.options.get_safe("with_fontconfig", False):
                gui_reqs.append("fontconfig::fontconfig")
            if self.settings.os in ["Linux", "FreeBSD"]:
                if not tools.cross_building(self, skip_x64_x86=True):
                    gui_reqs.append("xkbcommon::xkbcommon")
            if self.options.get_safe("opengl", "no") != "no":
                if self.settings.os == 'Linux' and self.options.with_mesa:
                    gui_reqs.append("mesa::mesa")
            if self.options.with_harfbuzz:
                gui_reqs.append("harfbuzz::harfbuzz")
            if self.options.with_libjpeg == "libjpeg-turbo":
                gui_reqs.append("libjpeg-turbo::libjpeg-turbo")
            if self.options.with_libjpeg == "libjpeg":
                gui_reqs.append("libjpeg::libjpeg")
            _create_module("Gui", gui_reqs)
        if self.options.with_sqlite3:
            _create_plugin("QSQLiteDriverPlugin", "qsqlite", "sqldrivers", ["sqlite3::sqlite3"])
        if self.options.with_pq:
            _create_plugin("QPSQLDriverPlugin", "qsqlpsql", "sqldrivers", ["libpq::libpq"])
        if self.options.get_safe("with_mysql", False):
            _create_plugin("QMySQLDriverPlugin", "qsqlmysql", "sqldrivers", ["libmysqlclient::libmysqlclient"])
        if self.options.with_odbc:
            if self.settings.os != "Windows":
                _create_plugin("QODBCDriverPlugin", "qsqlodbc", "sqldrivers", ["odbc::odbc"])
        networkReqs = []
        if self.options.openssl:
            networkReqs.append("openssl::openssl")
        _create_module("Network", networkReqs)
        _create_module("Sql")
        _create_module("Test")
        if self.options.widgets:
            _create_module("Widgets", ["Gui"])
        if self.options.gui and self.options.widgets:
            _create_module("PrintSupport", ["Gui", "Widgets"])
        if self.options.get_safe("opengl", "no") != "no" and self.options.gui:
            _create_module("OpenGL", ["Gui"])
        if self.options.widgets and self.options.get_safe("opengl", "no") != "no":
            _create_module("OpenGLExtensions", ["Gui"])
        _create_module("DBus")
        _create_module("Concurrent")
        _create_module("Xml")

        if self.options.qtdeclarative:
            _create_module("Qml", ["Network"])
            self.cpp_info.components["qtQml"].build_modules["cmake_find_package"].append(self._cmake_qt5_private_file("Qml"))
            self.cpp_info.components["qtQml"].build_modules["cmake_find_package_multi"].append(self._cmake_qt5_private_file("Qml"))
            _create_module("QmlModels", ["Qml"])
            self.cpp_info.components["qtQmlImportScanner"].names["cmake_find_package"] = "QmlImportScanner" # this is an alias for Qml and there to integrate with existing consumers
            self.cpp_info.components["qtQmlImportScanner"].names["cmake_find_package_multi"] = "QmlImportScanner"
            self.cpp_info.components["qtQmlImportScanner"].requires = _get_corrected_reqs(["Qml"])
            if self.options.gui:
                _create_module("Quick", ["Gui", "Qml", "QmlModels"])
                if self.options.widgets:
                    _create_module("QuickWidgets", ["Gui", "Qml", "Quick", "Widgets"])
                _create_module("QuickShapes", ["Gui", "Qml", "Quick"])
            _create_module("QmlWorkerScript", ["Qml"])
            _create_module("QuickTest", ["Test"])

        if self.options.qttools and self.options.gui and self.options.widgets:
            _create_module("UiPlugin", ["Gui", "Widgets"])
            self.cpp_info.components["qtUiPlugin"].libs = [] # this is a collection of abstract classes, so this is header-only
            self.cpp_info.components["qtUiPlugin"].libdirs = []
            _create_module("UiTools", ["UiPlugin", "Gui", "Widgets"])
            _create_module("Designer", ["Gui", "UiPlugin", "Widgets", "Xml"])
            _create_module("Help", ["Gui", "Sql", "Widgets"])

        if self.options.qtquick3d and self.options.gui:
            _create_module("Quick3DUtils", ["Gui"])
            _create_module("Quick3DAssetImport", ["Gui", "Qml", "Quick3DUtils"])
            _create_module("Quick3DRuntimeRender", ["Gui", "Quick", "Quick3DAssetImport", "Quick3DUtils", "ShaderTools"])
            _create_module("Quick3D", ["Gui", "Qml", "Quick", "Quick3DRuntimeRender"])

        if self.options.qtquickcontrols2 and self.options.gui:
            _create_module("QuickControls2", ["Gui", "Quick"])
            _create_module("QuickTemplates2", ["Gui", "Quick"])

        if self.options.qtsvg and self.options.gui:
            _create_module("Svg", ["Gui"])

        if self.options.qtwayland and self.options.gui:
            _create_module("WaylandClient", ["Gui", "wayland::wayland-client"])
            _create_module("WaylandCompositor", ["Gui", "wayland::wayland-server"])

        if self.options.qtlocation:
            _create_module("Positioning")
            _create_module("Location", ["Gui", "Quick"])
            _create_plugin("QGeoServiceProviderFactoryMapbox", "qtgeoservices_mapbox", "geoservices", [])
            _create_plugin("QGeoServiceProviderFactoryMapboxGL", "qtgeoservices_mapboxgl", "geoservices", [])
            _create_plugin("GeoServiceProviderFactoryEsri", "qtgeoservices_esri", "geoservices", [])
            _create_plugin("QGeoServiceProviderFactoryItemsOverlay", "qtgeoservices_itemsoverlay", "geoservices", [])
            _create_plugin("QGeoServiceProviderFactoryNokia", "qtgeoservices_nokia", "geoservices", [])
            _create_plugin("QGeoServiceProviderFactoryOsm", "qtgeoservices_osm", "geoservices", [])
            _create_plugin("QGeoPositionInfoSourceFactoryGeoclue", "qtposition_geoclue", "position", [])
            _create_plugin("QGeoPositionInfoSourceFactoryGeoclue2", "qtposition_geoclue2", "position", [])
            _create_plugin("QGeoPositionInfoSourceFactoryPoll", "qtposition_positionpoll", "position", [])
            _create_plugin("QGeoPositionInfoSourceFactorySerialNmea", "qtposition_serialnmea", "position", [])

        if self.options.qtwebchannel:
            _create_module("WebChannel", ["Qml"])

        if self.options.qtwebengine:
            _create_module("WebEngineCore", ["Gui", "Quick", "WebChannel", "Positioning", "expat::expat", "opus::libopus"])
            _create_module("WebEngine", ["WebEngineCore"])
            _create_module("WebEngineWidgets", ["WebEngineCore", "Quick", "PrintSupport", "Widgets", "Gui", "Network"])

        if self.options.qtserialport:
            _create_module("SerialPort")

        if self.options.qtserialbus:
            _create_module("SerialBus", ["SerialPort"])
            _create_plugin("PassThruCanBusPlugin", "qtpassthrucanbus", "canbus", [])
            _create_plugin("PeakCanBusPlugin", "qtpeakcanbus", "canbus", [])
            _create_plugin("SocketCanBusPlugin", "qtsocketcanbus", "canbus", [])
            _create_plugin("TinyCanBusPlugin", "qttinycanbus", "canbus", [])
            _create_plugin("VirtualCanBusPlugin", "qtvirtualcanbus", "canbus", [])

        if self.options.qtsensors:
            _create_module("Sensors")
            _create_plugin("genericSensorPlugin", "qtsensors_generic", "sensors", [])
            _create_plugin("IIOSensorProxySensorPlugin", "qtsensors_iio-sensor-proxy", "sensors", [])
            if self.settings.os == "Linux":
                _create_plugin("LinuxSensorPlugin", "qtsensors_linuxsys", "sensors", [])
            _create_plugin("QtSensorGesturePlugin", "qtsensorgestures_plugin", "sensorgestures", [])
            _create_plugin("QShakeSensorGesturePlugin", "qtsensorgestures_shakeplugin", "sensorgestures", [])

        if self.options.qtscxml:
            _create_module("Scxml", ["Qml"])

        if self.options.qtpurchasing:
            _create_module("Purchasing")

        if self.options.qtcharts:
            _create_module("Charts", ["Gui", "Widgets"])

        if self.options.qt3d:
            _create_module("3DCore", ["Gui", "Network"])

            _create_module("3DRender", ["3DCore"])
            _create_plugin("DefaultGeometryLoaderPlugin", "defaultgeometryloader", "geometryloaders", [])
            _create_plugin("GLTFGeometryLoaderPlugin", "gltfgeometryloader", "geometryloaders", [])
            _create_plugin("GLTFSceneExportPlugin", "gltfsceneexport", "sceneparsers", [])
            _create_plugin("GLTFSceneImportPlugin", "gltfsceneimport", "sceneparsers", [])
            _create_plugin("OpenGLRendererPlugin", "openglrenderer", "renderers", [])
            _create_plugin("Scene2DPlugin", "scene2d", "renderplugins", [])

            _create_module("3DAnimation", ["3DRender", "3DCore", "Gui"])
            _create_module("3DInput", ["3DCore", "GamePad", "Gui"])
            _create_module("3DLogic", ["3DCore", "Gui"])
            _create_module("3DExtras", ["3DRender", "3DInput", "3DLogic", "3DCore", "Gui"])
            _create_module("3DQuick", ["3DCore", "Quick", "Gui", "Qml"])
            _create_module("3DQuickAnimation", ["3DAnimation", "3DRender", "3DQuick", "3DCore", "Gui", "Qml"])
            _create_module("3DQuickExtras", ["3DExtras", "3DInput", "3DQuick", "3DRender", "3DLogic", "3DCore", "Gui", "Qml"])
            _create_module("3DQuickInput", ["3DInput", "3DQuick", "3DCore", "Gui", "Qml"])
            _create_module("3DQuickRender", ["3DRender", "3DQuick", "3DCore", "Gui", "Qml"])
            _create_module("3DQuickScene2D", ["3DRender", "3DQuick", "3DCore", "Gui", "Qml"])

        if self.options.qtgamepad:
            _create_module("Gamepad", ["Gui"])
            if self.settings.os == "Linux":
                _create_plugin("QEvdevGamepadBackendPlugin", "evdevgamepad", "gamepads", [])
            if self.settings.os == "Macos":
                _create_plugin("QDarwinGamepadBackendPlugin", "darwingamepad", "gamepads", [])
            if self.settings.os =="Windows":
                _create_plugin("QXInputGamepadBackendPlugin", "xinputgamepad", "gamepads", [])

        if self.options.qtmultimedia:
            multimedia_reqs = ["Network", "Gui"]
            if self.options.get_safe("with_libalsa", False):
                multimedia_reqs.append("libalsa::libalsa")
            if self.options.with_openal:
                multimedia_reqs.append("openal::openal")
            _create_module("Multimedia", multimedia_reqs)
            _create_module("MultimediaWidgets", ["Multimedia", "Widgets", "Gui"])
            if self.options.qtdeclarative and self.options.gui:
                _create_module("MultimediaQuick", ["Multimedia", "Quick"])
            _create_plugin("QM3uPlaylistPlugin", "qtmultimedia_m3u", "playlistformats", [])
            if self.options.with_gstreamer:
                _create_module("MultimediaGstTools", ["Multimedia", "MultimediaWidgets", "Gui", "gstreamer::gstreamer"])
                _create_plugin("QGstreamerAudioDecoderServicePlugin", "gstaudiodecoder", "mediaservice", [])
                _create_plugin("QGstreamerCaptureServicePlugin", "gstmediacapture", "mediaservice", [])
                _create_plugin("QGstreamerPlayerServicePlugin", "gstmediaplayer", "mediaservice", [])
            if self.settings.os == "Linux":
                _create_plugin("CameraBinServicePlugin", "gstcamerabin", "mediaservice", [])
                _create_plugin("QAlsaPlugin", "qtaudio_alsa", "audio", [])
            if self.settings.os == "Windows":
                _create_plugin("AudioCaptureServicePlugin", "qtmedia_audioengine", "mediaservice", [])
                _create_plugin("DSServicePlugin", "dsengine", "mediaservice", [])
                _create_plugin("QWindowsAudioPlugin", "qtaudio_windows", "audio", [])
            if self.settings.os == "Macos":
                _create_plugin("AudioCaptureServicePlugin", "qtmedia_audioengine", "mediaservice", [])
                _create_plugin("AVFMediaPlayerServicePlugin", "qavfmediaplayer", "mediaservice", [])
                _create_plugin("AVFServicePlugin", "qavfcamera", "mediaservice", [])
                _create_plugin("CoreAudioPlugin", "qtaudio_coreaudio", "audio", [])

        if self.options.qtwebsockets:
            _create_module("WebSockets", ["Network"])

        if self.options.qtconnectivity:
            _create_module("Bluetooth", ["Network"])
            _create_module("Nfc", [])

        if self.options.qtdatavis3d:
            _create_module("DataVisualization", ["Gui"])

        if self.options.qtnetworkauth:
            _create_module("NetworkAuth", ["Network"])

        if self.settings.os != "Windows":
            self.cpp_info.components["qtCore"].cxxflags.append("-fPIC")

        if self.options.get_safe("qtx11extras"):
            _create_module("X11Extras")

        if self.options.qtremoteobjects:
            _create_module("RemoteObjects")

        if self.options.qtwinextras:
            _create_module("WinExtras")

        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.components["qtCore"].system_libs.append("version")  # qtcore requires "GetFileVersionInfoW" and "VerQueryValueW" which are in "Version.lib" library
                self.cpp_info.components["qtCore"].system_libs.append("winmm")    # qtcore requires "__imp_timeSetEvent" which is in "Winmm.lib" library
                self.cpp_info.components["qtCore"].system_libs.append("netapi32") # qtcore requires "NetApiBufferFree" which is in "Netapi32.lib" library
                self.cpp_info.components["qtCore"].system_libs.append("userenv")  # qtcore requires "__imp_GetUserProfileDirectoryW " which is in "UserEnv.Lib" library
                self.cpp_info.components["qtCore"].system_libs.append("ws2_32")  # qtcore requires "WSAStartup " which is in "Ws2_32.Lib" library
                self.cpp_info.components["qtNetwork"].system_libs.append("dnsapi")  # qtnetwork from qtbase requires "DnsFree" which is in "Dnsapi.lib" library
                self.cpp_info.components["qtNetwork"].system_libs.append("iphlpapi")

            if self.settings.os == "Macos":
                self.cpp_info.components["qtCore"].frameworks.append("IOKit")     # qtcore requires "_IORegistryEntryCreateCFProperty", "_IOServiceGetMatchingService" and much more which are in "IOKit" framework
                self.cpp_info.components["qtCore"].frameworks.append("Cocoa")     # qtcore requires "_OBJC_CLASS_$_NSApplication" and more, which are in "Cocoa" framework
                self.cpp_info.components["qtCore"].frameworks.append("Security")  # qtcore requires "_SecRequirementCreateWithString" and more, which are in "Security" framework
                self.cpp_info.components["qtNetwork"].frameworks.append("SystemConfiguration")
                self.cpp_info.components["qtNetwork"].frameworks.append("GSS")

        self.cpp_info.components["qtCore"].builddirs.append(os.path.join("bin","archdatadir","bin"))
        self.cpp_info.components["qtCore"].build_modules["cmake_find_package"].append(self._cmake_executables_file)
        self.cpp_info.components["qtCore"].build_modules["cmake_find_package_multi"].append(self._cmake_executables_file)
        self.cpp_info.components["qtCore"].build_modules["cmake_find_package"].append(self._cmake_qt5_private_file("Core"))
        self.cpp_info.components["qtCore"].build_modules["cmake_find_package_multi"].append(self._cmake_qt5_private_file("Core"))

        self.cpp_info.components["qtGui"].build_modules["cmake_find_package"].append(self._cmake_qt5_private_file("Gui"))
        self.cpp_info.components["qtGui"].build_modules["cmake_find_package_multi"].append(self._cmake_qt5_private_file("Gui"))

        for m in os.listdir(os.path.join("lib", "cmake")):
            module = os.path.join("lib", "cmake", m, "%sMacros.cmake" % m)
            component_name = m.replace("Qt5", "qt")
            if os.path.isfile(module):
                self.cpp_info.components[component_name].build_modules["cmake_find_package"].append(module)
                self.cpp_info.components[component_name].build_modules["cmake_find_package_multi"].append(module)
            self.cpp_info.components[component_name].builddirs.append(os.path.join("lib", "cmake", m))

        objects_dirs = glob.glob(os.path.join(self.package_folder, "lib", "objects-*/"))
        for object_dir in objects_dirs:
            for m in os.listdir(object_dir):
                submodules_dir = os.path.join(object_dir, m)
                component = "qt" + m[:m.find("_")]
                for sub_dir in os.listdir(submodules_dir):
                    submodule_dir = os.path.join(submodules_dir, sub_dir)
                    obj_files = [os.path.join(submodule_dir, file) for file in os.listdir(submodule_dir)]
                    self.cpp_info.components[component].exelinkflags.extend(obj_files)
                    self.cpp_info.components[component].sharedlinkflags.extend(obj_files)

    @staticmethod
    def _remove_duplicate(l):
        seen = set()
        seen_add = seen.add
        for element in itertools.filterfalse(seen.__contains__, l):
            seen_add(element)
            yield element

    def _gather_libs(self, p):
        if not p in self.deps_cpp_info.deps:
            return []
        libs = ["-l" + i for i in self.deps_cpp_info[p].libs + self.deps_cpp_info[p].system_libs]
        if tools.is_apple_os(self.settings.os):
            libs += ["-framework " + i for i in self.deps_cpp_info[p].frameworks]
        libs += self.deps_cpp_info[p].sharedlinkflags
        for dep in self.deps_cpp_info[p].public_deps:
            libs += self._gather_libs(dep)
        return self._remove_duplicate(libs)
