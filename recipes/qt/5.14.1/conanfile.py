import os
import shutil
import itertools

import configparser
from conans import ConanFile, tools, __version__ as conan_version
from conans.errors import ConanInvalidConfiguration
from conans.model import Generator
from conans.tools import Version, os_info


class qt(Generator):
    @property
    def filename(self):
        return "qt.conf"

    @property
    def content(self):
        return "[Paths]\nPrefix = %s\n" % self.conanfile.deps_cpp_info["qt"].rootpath.replace("\\", "/")


def _getsubmodules():
    config = configparser.ConfigParser()
    config.read('qtmodules.conf')
    res = {}
    assert config.sections()
    for s in config.sections():
        section = str(s)
        assert section.startswith("submodule ")
        assert section.count('"') == 2
        modulename = section[section.find('"') + 1: section.rfind('"')]
        status = str(config.get(section, "status"))
        if status != "obsolete" and status != "ignore":
            res[modulename] = {"branch": str(config.get(section, "branch")), "status": status,
                               "path": str(config.get(section, "path")), "depends": []}
            if config.has_option(section, "depends"):
                res[modulename]["depends"] = [str(i) for i in config.get(section, "depends").split()]
    return res


class QtConan(ConanFile):

    _submodules = _getsubmodules()

    generators = "pkg_config"
    name = "qt"
    description = "Qt is a cross-platform framework for graphical user interfaces."
    topics = ("conan", "qt", "ui")
    url = "https://github.com/bincrafters/conan-qt"
    homepage = "https://www.qt.io"
    license = "LGPL-3.0"
    exports = ["qtmodules.conf", "patches/*.diff"]
    settings = "os", "arch", "compiler", "build_type"

    library_source = {
        "not_used": "-no-",
        "qt": "-qt-",
        "system": "-system-"
    }  

    library_sources = list(library_source.keys())

    options = dict({
        "shared": [True, False],
        "commercial": [True, False],

        "opengl": ["no", "es2", "desktop", "dynamic"],
        "openssl": [True, False],
        "with_pcre2": [True, False],
        "with_glib": [True, False],
        # "with_libiconv": [True, False],  # Qt tests failure "invalid conversion from const char** to char**"
        "with_doubleconversion": library_sources,
        "with_freetype": library_sources,
        "with_fontconfig": [True, False],
        "with_icu": [True, False],
        "with_harfbuzz": library_sources,
        "with_libjpeg": library_sources,
        "with_libpng": library_sources,
        "with_sqlite3": library_sources,
        "with_mysql": [True, False],
        "with_pq": [True, False],
        "with_odbc": [True, False],
        "with_sdl2": [True, False],
        "with_libalsa": [True, False],
        "with_mesa": [True, False],
        "with_openal": [True, False],
        "with_zstd": [True, False],

        "GUI": [True, False],
        "widgets": [True, False],

        "device": "ANY",
        "cross_compile": "ANY",
        "sysroot": "ANY",
        "config": "ANY",
        "multiconfiguration": [True, False],
        "with_builtin_libs": [True, False],
    }, **{module: [True, False] for module in _submodules if module != 'qtbase'}
    )
    no_copy_source = True
    default_options = dict({
        "shared": True,
        "commercial": False,
        "opengl": "desktop",
        "openssl": True,
        "with_pcre2": True,
        "with_glib": True,
        # "with_libiconv": True,
        "with_doubleconversion": "system",
        "with_freetype": "system",
        "with_fontconfig": True,
        "with_icu": True,
        "with_harfbuzz": "system",
        "with_libjpeg": "system",
        "with_libpng": "system",
        "with_sqlite3": "system",
        "with_mysql": True,
        "with_pq": True,
        "with_odbc": True,
        "with_sdl2": True,
        "with_libalsa": False,
        "with_mesa": True,
        "with_openal": True,
        "with_zstd": True,

        "GUI": True,
        "widgets": True,

        "device": None,
        "cross_compile": None,
        "sysroot": None,
        "config": None,
        "multiconfiguration": False,
        "with_builtin_libs": False,
        "libxcb:shared": True,
    }, **{module: False for module in _submodules if module != 'qtbase'}
    )
    requires = "zlib/1.2.11"
    short_paths = True

    _xcb_packages = {
        "libxcb": "1.13.1",
        "libx11": "1.6.8",
        "xcb-util": "0.4.0",
        "xcb-util-wm": "0.4.0",
        "xcb-util-image": "0.4.0",
        "xcb-util-keysyms": "0.4.0",
        "xcb-util-renderutil": "0.3.9",
        "libxcursor": "1.2.0"
    }

    def build_requirements(self):
        if tools.os_info.is_windows and self.settings.compiler == "Visual Studio":
            self.build_requires("jom/1.1.3")
        if self.settings.os == 'Linux':
            if not tools.which('pkg-config'):
                self.build_requires('pkg-config_installer/0.29.2')
        if self.options.qtwebengine:
            # gperf, bison, flex, python >= 2.7.5 & < 3
            if not tools.which("bison"):
                self.build_requires("bison_installer/3.3.2")
            if not tools.which("gperf"):
                self.build_requires("gperf_installer/3.1")
            if not tools.which("flex"):
                self.build_requires("flex_installer/2.6.4")

            def _check_python_version():
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
                cmd_v = "{} --version".format(python_exe)
                self.run(cmd_v, output=mybuf)
                verstr = mybuf.getvalue().strip().split('Python ')[1]
                if verstr.endswith('+'):
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
                           "{})".format(verstr, v_min, v_max))
                    raise ConanInvalidConfiguration(msg)

            try:
                _check_python_version()
            except ConanInvalidConfiguration as e:
                if tools.os_info.is_windows:
                    raise e
                self.output.info("Python 2 not detected in path. Trying to install it")
                tools.SystemPackageTool().install(["python2", "python"])
                _check_python_version()

    def config_options(self):
        if self.settings.os != "Linux":
            self.options.with_icu = False

    def configure(self):
        if conan_version < Version("1.20.0"):
            raise ConanInvalidConfiguration("This recipe needs at least conan 1.20.0, please upgrade.")
        if self.settings.os != 'Linux':
        #     self.options.with_libiconv = False
            self.options.with_fontconfig = False
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version.value) < "5.3":
            self.options.with_mysql = False
        if self.settings.os == "Windows":
            self.options.with_mysql = False
            if not self.options.shared and self.options.with_icu:
                raise ConanInvalidConfiguration("icu option is not supported on windows in static build. see QTBUG-77120.")

        if self.options.widgets and not self.options.GUI:
            raise ConanInvalidConfiguration("using option qt:widgets without option qt:GUI is not possible. "
                                            "You can either disable qt:widgets or enable qt:GUI")
        if not self.options.GUI:
            self.options.opengl = "no"
            self.options.with_freetype = "not_used"
            self.options.with_fontconfig = False
            self.options.with_harfbuzz = "not_used"
            self.options.with_libjpeg = "not_used"
            self.options.with_libpng = "not_used"

        if not self.options.qtgamepad:
            self.options.with_sdl2 = False

        if not self.options.qtmultimedia:
            self.options.with_libalsa = False
            self.options.with_openal = False

        if self.settings.os != "Linux":
            self.options.with_libalsa = False

        if self.options.qtwebengine:
            if not self.options.shared:
                raise ConanInvalidConfiguration("Static builds of Qt Webengine are not supported")

            if tools.cross_building(self.settings, skip_x64_x86=True):
                raise ConanInvalidConfiguration("Cross compiling Qt WebEngine is not supported")

            if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
                raise ConanInvalidConfiguration("Compiling Qt WebEngine with gcc < 5 is not supported")

        if self.settings.os == "Android" and self.options.opengl == "desktop":
            raise ConanInvalidConfiguration("OpenGL desktop is not supported on Android. Consider using OpenGL es2")

        if self.settings.os != "Windows" and self.options.opengl == "dynamic":
            raise ConanInvalidConfiguration("Dynamic OpenGL is supported only on Windows.")

        if self.options.with_fontconfig and not self.options.with_freetype:
            raise ConanInvalidConfiguration("with_fontconfig cannot be enabled if with_freetype is disabled.")

        if self.settings.os == "Macos":
            del self.settings.os.version

        if self.options.multiconfiguration:
            del self.settings.build_type

        if self.options.with_doubleconversion == "not_used" and str(self.settings.compiler.libcxx) != "libc++":
            raise ConanInvalidConfiguration('Qt without libc++ needs qt:with_doubleconversion. '
                                            'Either enable qt:with_doubleconversion or switch to libc++')

        if tools.os_info.is_linux:
            if self.options.qtwebengine:
                self.options.with_fontconfig = True

        assert self.version == self._submodules['qtbase']['branch']

        def _enablemodule(mod):
            if mod != 'qtbase':
                setattr(self.options, mod, True)
            for req in self._submodules[mod]["depends"]:
                _enablemodule(req)

        for module in self._submodules:
            if module != 'qtbase' and getattr(self.options, module):
                _enablemodule(module)

    def requirements(self):
        if self.options.openssl:
            self.requires("openssl/1.1.1d")
        if self.options.with_pcre2:
            self.requires("pcre2/10.33")

        if self.options.multiconfiguration or self.options.with_builtin_libs:
            self.options.with_doubleconversion = "qt"
            self.options.with_freetype = "qt"
            self.options.with_harfbuzz = "qt"
            self.options.with_libjpeg = "qt"
            self.options.with_libpng= "qt"
            self.options.with_sqlite3 = "qt"

        if self.options.with_glib:
            self.requires("glib/2.64.0")
        # if self.options.with_libiconv:
        #     self.requires("libiconv/1.16")
        if self.options.with_doubleconversion == "system":
            self.requires("double-conversion/3.1.5")
        if self.options.with_freetype == "system":
            self.requires("freetype/2.10.1")
        if self.options.with_fontconfig:
            self.requires("fontconfig/2.13.91")
        if self.options.with_icu:
            self.requires("icu/64.2")
        if self.options.with_harfbuzz == "system":
            self.requires("harfbuzz/2.6.4")
        if self.options.with_libjpeg == "system":
            self.requires("libjpeg/9d")
        if self.options.with_libpng == "system":
            self.requires("libpng/1.6.37")
        if self.options.with_sqlite3 == "system":
            self.requires("sqlite3/3.31.0")
            self.options["sqlite3"].enable_column_metadata = True
        if self.options.with_mysql:
            self.requires("libmysqlclient/8.0.17")
        if self.options.with_pq:
            self.requires("libpq/11.5")
        if self.options.with_odbc:
            if self.settings.os != "Windows":
                self.requires("odbc/2.3.7")
        if self.options.with_sdl2:
            self.requires("sdl2/2.0.10")
        if self.options.with_openal:
            self.requires("openal/1.20.1")
        if self.options.with_libalsa:
            self.requires("libalsa/1.1.9")
        if self.options.GUI and self.settings.os == "Linux":
            for p in self._xcb_packages:
                self.requires("%s/%s" % (p, self._xcb_packages[p]))
            if not tools.cross_building(self.settings, skip_x64_x86=True):
                self.requires("xkbcommon/0.10.0")
        if self.options.with_zstd:
            self.requires("zstd/1.4.4")
        if self.options.qtwebengine and self.settings.os == "Linux":
            self.requires("libx11/1.6.8")
            self.requires("libdrm/2.4.100")
            self.requires("libxcomposite/0.4.5")
            self.requires("libxcursor/1.2.0")
            self.requires("libxi/1.7.10")
            self.requires("libxtst/1.2.3")
            self.requires("libxrandr/1.5.2")
            self.requires("libxscrnsaver/1.2.3")
            self.requires("expat/2.2.9")
            #self.requires("ffmpeg/4.2@bincrafters/stable")
            self.requires("opus/1.3.1")

        if self.options.opengl in ["desktop", "es2"]:
            if self.settings.os == 'Linux' and self.options.with_mesa:
                self.requires('mesa/19.3.1')

    def system_requirements(self):
        pack_names = []
        if tools.os_info.is_linux:
            if tools.os_info.with_apt:
                if self.options.qtwebengine:
                    pack_names.append("libnss3-dev")
                    pack_names.append("libdbus-1-dev")

        if pack_names:
            installer = tools.SystemPackageTool()
            for item in pack_names:
                installer.install(item)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        shutil.move("qt-everywhere-src-%s" % self.version, "qt5")

        for p in self.conan_data["patches"][self.version]:
            tools.patch(**p)

        if self.settings.os == "Linux":
            tools.replace_in_file(os.path.join(self.source_folder, "qt5", "qtbase", "mkspecs", "common", "linux.conf"),\
                                  "QMAKE_LIBS_OPENGL       = -lGL",\
                                  "QMAKE_LIBS_OPENGL       = -lGL -ldrm -lxcb-dri3")

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
            return {"clang": "android-clang",
                    "gcc": "android-g++"}.get(str(self.settings.compiler))

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
                               "x86_64": "winrt-x64-msvc2017"}
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

        return None

    def build(self):
        args = ["-confirm-license", "-silent", "-nomake examples", "-nomake tests", "-no-feature-accessibility",
                "-prefix %s" % self.package_folder]
        if self.options.commercial:
            args.append("-commercial")
        else:
            args.append("-opensource")
        if not self.options.GUI:
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
            if module != 'qtbase' and not getattr(self.options, module) \
                    and os.path.isdir(os.path.join(self.source_folder, 'qt5', self._submodules[module]['path'])):
                args.append("-skip " + module)

        args.append("--zlib=system")

        # openGL
        if self.options.opengl == "no":
            args += ["-no-opengl"]
        elif self.options.opengl == "es2":
            args += ["-opengl es2"]
        elif self.options.opengl == "desktop":
            args += ["-opengl desktop"]
        elif self.options.opengl == "dynamic":
            args += ["-opengl dynamic"]

        # openSSL
        if not self.options.openssl:
            args += ["-no-openssl"]
        else:
            if self.options["openssl"].shared:
                args += ["-openssl-runtime"]
            else:
                args += ["-openssl-linked"]

        # args.append("--iconv=" + ("gnu" if self.options.with_libiconv else "no"))

        args.append("--glib=" + ("yes" if self.options.with_glib else "no"))
        args.append("--pcre=" + ("system" if self.options.with_pcre2 else "qt"))
        args.append("--fontconfig=" + ("yes" if self.options.with_fontconfig else "no"))
        args.append("--icu=" + ("yes" if self.options.with_icu else "no"))
        args.append("--sql-mysql=" + ("yes" if self.options.with_mysql else "no"))
        args.append("--sql-psql=" + ("yes" if self.options.with_pq else "no"))
        args.append("--sql-odbc=" + ("yes" if self.options.with_odbc else "no"))
        args.append("--zstd=" + ("yes" if self.options.with_zstd else "no"))

        if self.options.qtmultimedia:
            args.append("--alsa=" + ("yes" if self.options.with_libalsa else "no"))

        for opt, conf_arg in [
                              ("with_doubleconversion", "doubleconversion"),
                              ("with_freetype", "freetype"),
                              ("with_harfbuzz", "harfbuzz"),
                              ("with_libjpeg", "libjpeg"),
                              ("with_libpng", "libpng"),
                              ("with_sqlite3", "sqlite")]:
            args += [self.library_source[str(getattr(self.options, opt))] + conf_arg]

        libmap = [("zlib", "ZLIB"),
                  ("openssl", "OPENSSL"),
                  ("pcre2", "PCRE2"),
                  ("glib", "GLIB"),
                  # ("libiconv", "ICONV"),
                  ("double-conversion", "DOUBLECONVERSION"),
                  ("freetype", "FREETYPE"),
                  ("fontconfig", "FONTCONFIG"),
                  ("icu", "ICU"),
                  ("harfbuzz", "HARFBUZZ"),
                  ("libjpeg", "LIBJPEG"),
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
                if package == 'freetype':
                    args.append("\"%s_INCDIR=%s\"" % (var, self.deps_cpp_info[package].include_paths[-1]))

                args.append("\"%s_LIBS=%s\"" % (var, " ".join(self._gather_libs(package))))

        for package in self.deps_cpp_info.deps:
            args += ["-I " + s for s in self.deps_cpp_info[package].include_paths]
            args += ["-D " + s for s in self.deps_cpp_info[package].defines]
            args += ["-L " + s for s in self.deps_cpp_info[package].lib_paths]

        if 'libmysqlclient' in self.deps_cpp_info.deps:
            args.append("-mysql_config " + os.path.join(self.deps_cpp_info['libmysqlclient'].rootpath, "bin", "mysql_config"))
        if 'libpq' in self.deps_cpp_info.deps:
            args.append("-psql_config " + os.path.join(self.deps_cpp_info['libpq'].rootpath, "bin", "pg_config"))
        if self.settings.os == "Linux":
            if self.options.GUI:
                args.append("-system-xcb")
        elif self.settings.os == "Macos":
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

        def _getenvpath(var):
            val = os.getenv(var)
            if val and tools.os_info.is_windows:
                val = val.replace("\\", "/")
                os.environ[var] = val
            return val

        value = _getenvpath('CC')
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
            args += ['-qt-webengine-ffmpeg',
                     '-system-webengine-opus']

        if self.options.config:
            args.append(str(self.options.config))

        for package in ['libxcomposite', 'libxcursor', 'libxi', 'libxtst', 'mesa'] + [p for p in self._xcb_packages]:
            def _gather_pc_files(package):
                if package in self.deps_cpp_info.deps:
                    lib_path = self.deps_cpp_info[package].rootpath
                    for dirpath, _, filenames in os.walk(lib_path):
                        for filename in filenames:
                            if filename.endswith('.pc'):
                                shutil.copyfile(os.path.join(dirpath, filename), filename)
                                tools.replace_prefix_in_pc_file(filename, lib_path)
                    for dep in self.deps_cpp_info[package].public_deps:
                        _gather_pc_files(dep)
            _gather_pc_files(package)

        with tools.vcvars(self.settings):
            build_env = {"MAKEFLAGS": "j%d" % tools.cpu_count(), "PKG_CONFIG_PATH": [os.getcwd()]}
            if self.options.qtwebengine:
                if self.settings.compiler in ['gcc', 'clang']:
                    i_path = []
                    l_path = []
                    for p in ['fontconfig', 'libxcursor', 'libxi', 'libxtst', 'libxrandr', 'libxscrnsaver', 'libxcomposite', 'zlib', 'libxdamage']:
                        i_path.extend(self._gather_include_paths(p))
                        l_path.extend(self._gather_lib_paths(p))
                    build_env['C_INCLUDE_PATH'] = os.pathsep.join(i_path)
                    build_env['CPLUS_INCLUDE_PATH'] = os.pathsep.join(i_path)
                    build_env['LIBRARY_PATH'] = os.pathsep.join(l_path)
            with tools.environment_append(build_env):
                try:
                    self.run("%s/qt5/configure %s" % (self.source_folder, " ".join(args)), run_environment=True)
                finally:
                    self.output.info(open('config.log', errors='backslashreplace').read())

                if self.settings.compiler == "Visual Studio":
                    make = "jom"
                elif tools.os_info.is_windows:
                    make = "mingw32-make"
                else:
                    make = "make"
                self.run(make, run_environment=True)
                self.run("%s install" % make)

        with open('qtbase/bin/qt.conf', 'w') as f:
            f.write('[Paths]\nPrefix = ..')

    def package(self):
        self.copy("bin/qt.conf", src="qtbase")

    def package_id(self):
        del self.info.options.cross_compile
        del self.info.options.sysroot

    def package_info(self):
        libs = [
          "Qt5Core",
          "Qt5DBus",
          "Qt5Gui",
          "Qt5Network",
          "Qt5OpenGL",
          "Qt5PrintSupport",
          "Qt5Sql",
          "Qt5Svg",
          "Qt5Widgets",
          "Qt5Xml"
        ]
        if self.options.qtmultimedia:
            libs.extend([
                "Qt5Multimedia",
                "Qt5MultimediaWidgets"
                ])
        if os_info.is_linux:
            libs.append("Qt5X11Extras")
        self.cpp_info.libdirs.append('lib')
        self.cpp_info.libs = [lib for lib in libs]
        self.env_info.CMAKE_PREFIX_PATH.append(self.package_folder)

    @staticmethod
    def _remove_duplicate(l):
        seen = set()
        seen_add = seen.add
        for element in itertools.filterfalse(seen.__contains__, l):
            seen_add(element)
            yield element

    def _gather_libs(self, p):
        libs = ["-l" + i for i in self.deps_cpp_info[p].libs + self.deps_cpp_info[p].system_libs]
        if tools.is_apple_os(self.settings.os):
            libs += ["-framework " + i for i in self.deps_cpp_info[p].frameworks]
        libs += self.deps_cpp_info[p].sharedlinkflags
        for dep in self.deps_cpp_info[p].public_deps:
            libs += self._gather_libs(dep)
        return self._remove_duplicate(libs)

    def _gather_lib_paths(self, p):
        lib_paths = self.deps_cpp_info[p].lib_paths
        for dep in self.deps_cpp_info[p].public_deps:
            lib_paths += self._gather_lib_paths(dep)
        return self._remove_duplicate(lib_paths)

    def _gather_include_paths(self, p):
        include_paths = self.deps_cpp_info[p].include_paths
        for dep in self.deps_cpp_info[p].public_deps:
            include_paths += self._gather_include_paths(dep)
        return self._remove_duplicate(include_paths)
