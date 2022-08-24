from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.microsoft import msvc_runtime_flag
from conan.errors import ConanInvalidConfiguration
from conans import tools, RunEnvironment
from conans.model import Generator
import configparser
import glob
import itertools
import os
import textwrap

required_conan_version = ">=1.43.0"


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
    "qtspeech", "qtnetworkauth", "qtremoteobjects", "qtwebglplugin", "qtlottie", "qtquicktimeline", "qtquick3d",
    "qtknx", "qtmqtt", "qtcoap", "qtopcua"]

    name = "qt"
    description = "Qt is a cross-platform framework for graphical user interfaces."
    topics = ("qt", "ui")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.qt.io"
    license = "LGPL-3.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "commercial": [True, False],

        "opengl": ["no", "es2", "desktop", "dynamic"],
        "with_vulkan": [True, False],
        "openssl": [True, False],
        "with_pcre2": [True, False],
        "with_glib": [True, False],
        # "with_libiconv": [True, False],  # QTBUG-84708 Qt tests failure "invalid conversion from const char** to char**"
        "with_doubleconversion": [True, False],
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
        "with_openal": [True, False],
        "with_zstd": [True, False],
        "with_gstreamer": [True, False],
        "with_pulseaudio": [True, False],
        "with_dbus": [True, False],
        "with_gssapi": [True, False],
        "with_atspi": [True, False],
        "with_md4c": [True, False],

        "gui": [True, False],
        "widgets": [True, False],

        "device": "ANY",
        "cross_compile": "ANY",
        "sysroot": "ANY",
        "config": "ANY",
        "multiconfiguration": [True, False]
    }
    options.update({module: [True, False] for module in _submodules})

    default_options = {
        "shared": False,
        "commercial": False,
        "opengl": "desktop",
        "with_vulkan": False,
        "openssl": True,
        "with_pcre2": True,
        "with_glib": False,
        # "with_libiconv": True, # QTBUG-84708
        "with_doubleconversion": True,
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
        "with_openal": True,
        "with_zstd": True,
        "with_gstreamer": False,
        "with_pulseaudio": False,
        "with_dbus": False,
        "with_gssapi": False,
        "with_atspi": False,
        "with_md4c": True,

        "gui": True,
        "widgets": True,

        "device": None,
        "cross_compile": None,
        "sysroot": None,
        "config": None,
        "multiconfiguration": False
    }
    default_options.update({module: False for module in _submodules})

    no_copy_source = True
    short_paths = True
    generators = "pkg_config"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export(self):
        self.copy("qtmodules%s.conf" % self.version)

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def build_requirements(self):
        if self._settings_build.os == "Windows" and self._is_msvc:
            self.build_requires("jom/1.1.3")
        if self.options.qtwebengine:
            self.build_requires("ninja/1.11.0")
            self.build_requires("nodejs/16.3.0")
            self.build_requires("gperf/3.1")
            # gperf, bison, flex, python >= 2.7.5 & < 3
            if self.settings.os != "Windows":
                self.build_requires("bison/3.7.6")
                self.build_requires("flex/2.6.4")
            else:
                self.build_requires("winflexbison/2.5.24")

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
            version = tools.scm.Version(self, verstr)
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

        if self.options.qtwayland:
            self.build_requires("wayland/1.21.0")

    def config_options(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_icu
            del self.options.with_fontconfig
            del self.options.with_libalsa
        if self.settings.compiler == "apple-clang":
            if tools.scm.Version(self, self.settings.compiler.version) < "10.0":
                raise ConanInvalidConfiguration("Old versions of apple sdk are not supported by Qt (QTBUG-76777)")
        if self.settings.compiler in ["gcc", "clang"]:
            if tools.scm.Version(self, self.settings.compiler.version) < "5.0":
                raise ConanInvalidConfiguration("qt 5.15.X does not support GCC or clang before 5.0")
        if self.settings.compiler in ["gcc", "clang"] and tools.scm.Version(self, self.settings.compiler.version) < "5.3":
            del self.options.with_mysql
        if self.settings.os == "Windows":
            self.options.with_mysql = False
            self.options.opengl = "dynamic"
            del self.options.with_gssapi
        if self.settings.os != "Linux":
            self.options.qtwayland = False
            self.options.with_atspi = False

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
            del self.options.with_md4c
        
        if not self.options.with_dbus:
            del self.options.with_atspi

        if not self.options.qtmultimedia:
            del self.options.with_libalsa
            del self.options.with_openal
            del self.options.with_gstreamer
            del self.options.with_pulseaudio

        if self.settings.os in ("FreeBSD", "Linux"):
            if self.options.qtwebengine:
                self.options.with_fontconfig = True
        else:
            del self.options.qtx11extras

        if self.options.multiconfiguration:
            del self.settings.build_type

        config = configparser.ConfigParser()
        config.read(os.path.join(self.recipe_folder, "qtmodules%s.conf" % self.version))
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
            if m not in submodules_tree:
                delattr(self.options, m)

        def _enablemodule(mod):
            if mod != "qtbase":
                setattr(self.options, mod, True)
            for req in submodules_tree[mod]["depends"]:
                _enablemodule(req)

        for module in self._submodules:
            if self.options.get_safe(module):
                _enablemodule(module)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, "11")
        if self.options.widgets and not self.options.gui:
            raise ConanInvalidConfiguration("using option qt:widgets without option qt:gui is not possible. "
                                            "You can either disable qt:widgets or enable qt:gui")

        if self.options.qtwebengine:
            if not self.options.shared:
                raise ConanInvalidConfiguration("Static builds of Qt WebEngine are not supported")

            if not (self.options.gui and self.options.qtdeclarative and self.options.qtlocation and self.options.qtwebchannel):
                raise ConanInvalidConfiguration("option qt:qtwebengine requires also qt:gui, qt:qtdeclarative, qt:qtlocation and qt:qtwebchannel")

            if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
                raise ConanInvalidConfiguration("Cross compiling Qt WebEngine is not supported")

            if self.settings.compiler == "gcc" and tools.scm.Version(self, self.settings.compiler.version) < "5":
                raise ConanInvalidConfiguration("Compiling Qt WebEngine with gcc < 5 is not supported")

        if self.settings.os == "Android" and self.options.get_safe("opengl", "no") == "desktop":
            raise ConanInvalidConfiguration("OpenGL desktop is not supported on Android. Consider using OpenGL es2")

        if self.settings.os != "Windows" and self.options.get_safe("opengl", "no") == "dynamic":
            raise ConanInvalidConfiguration("Dynamic OpenGL is supported only on Windows.")

        if self.options.get_safe("with_fontconfig", False) and not self.options.get_safe("with_freetype", False):
            raise ConanInvalidConfiguration("with_fontconfig cannot be enabled if with_freetype is disabled.")

        if not self.options.with_doubleconversion and str(self.settings.compiler.libcxx) != "libc++":
            raise ConanInvalidConfiguration("Qt without libc++ needs qt:with_doubleconversion. "
                                            "Either enable qt:with_doubleconversion or switch to libc++")

        if "MT" in self.settings.get_safe("compiler.runtime", default="") and self.options.shared:
            raise ConanInvalidConfiguration("Qt cannot be built as shared library with static runtime")

        if self.settings.compiler == "apple-clang":
            if tools.scm.Version(self, self.settings.compiler.version) < "10.0":
                raise ConanInvalidConfiguration("Old versions of apple sdk are not supported by Qt (QTBUG-76777)")
        if self.settings.compiler in ["gcc", "clang"]:
            if tools.scm.Version(self, self.settings.compiler.version) < "5.0":
                raise ConanInvalidConfiguration("qt 5.15.X does not support GCC or clang before 5.0")

        if self.options.get_safe("with_pulseaudio", default=False) and not self.options["pulseaudio"].with_glib:
            # https://bugreports.qt.io/browse/QTBUG-95952
            raise ConanInvalidConfiguration("Pulseaudio needs to be built with glib option or qt's configure script won't detect it")
        
        if self.settings.os in ['Linux', 'FreeBSD'] and self.options.with_gssapi:
            raise ConanInvalidConfiguration("gssapi cannot be enabled until conan-io/conan-center-index#4102 is closed")

    def requirements(self):
        self.requires("zlib/1.2.12")
        if self.options.openssl:
            self.requires("openssl/1.1.1q")
        if self.options.with_pcre2:
            self.requires("pcre2/10.40")
        if self.options.get_safe("with_vulkan"):
            self.requires("vulkan-loader/1.3.221")
            if tools.is_apple_os(self, self.settings.os):
                self.requires("moltenvk/1.1.10")
        if self.options.with_glib:
            self.requires("glib/2.73.2")
        # if self.options.with_libiconv: # QTBUG-84708
        #     self.requires("libiconv/1.16")# QTBUG-84708
        if self.options.with_doubleconversion:
            self.requires("double-conversion/3.2.0")
        if self.options.get_safe("with_freetype", False):
            self.requires("freetype/2.12.1")
        if self.options.get_safe("with_fontconfig", False):
            self.requires("fontconfig/2.13.93")
        if self.options.get_safe("with_icu", False):
            self.requires("icu/71.1")
        if self.options.get_safe("with_harfbuzz", False):
            self.requires("harfbuzz/4.4.1")
        if self.options.get_safe("with_libjpeg", False):
            if self.options.with_libjpeg == "libjpeg-turbo":
                self.requires("libjpeg-turbo/2.1.3")
            else:
                self.requires("libjpeg/9d")
        if self.options.get_safe("with_libpng", False):
            self.requires("libpng/1.6.37")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.39.2")
            self.options["sqlite3"].enable_column_metadata = True
        if self.options.get_safe("with_mysql", False):
            self.requires("libmysqlclient/8.0.29")
        if self.options.with_pq:
            self.requires("libpq/14.2")
        if self.options.with_odbc:
            if self.settings.os != "Windows":
                self.requires("odbc/2.3.9")
        if self.options.get_safe("with_openal", False):
            self.requires("openal/1.22.2")
        if self.options.get_safe("with_libalsa", False):
            self.requires("libalsa/1.2.7.2")
        if self.options.gui and self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system")
            self.requires("xkbcommon/1.4.1")
        if self.options.get_safe("opengl", "no") != "no":
            self.requires("opengl/system")
        if self.options.with_zstd:
            self.requires("zstd/1.5.2")
        if self.options.qtwebengine and self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("expat/2.4.8")
            self.requires("opus/1.3.1")
            self.requires("xorg-proto/2021.4")
            self.requires("libxshmfence/1.3")
            self.requires("nss/3.77")
            self.requires("libdrm/2.4.109")
        if self.options.get_safe("with_gstreamer", False):
            self.requires("gst-plugins-base/1.19.2")
        if self.options.get_safe("with_pulseaudio", False):
            self.requires("pulseaudio/14.2")
        if self.options.with_dbus:
            self.requires("dbus/1.12.20")
        if self.options.qtwayland:
            self.requires("wayland/1.21.0")
        if self.settings.os in ['Linux', 'FreeBSD'] and self.options.with_gssapi:
            self.requires("krb5/1.18.3") # conan-io/conan-center-index#4102
        if self.options.get_safe("with_atspi"):
            self.requires("at-spi2-core/2.45.1")
        if self.options.get_safe("with_md4c", False):
            self.requires("md4c/0.4.8")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination="qt5")

        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        for f in ["renderer", os.path.join("renderer", "core"), os.path.join("renderer", "platform")]:
            tools.files.replace_in_file(self, os.path.join(self.source_folder, "qt5", "qtwebengine", "src", "3rdparty", "chromium", "third_party", "blink", f, "BUILD.gn"),
                                  "  if (enable_precompiled_headers) {\n    if (is_win) {",
                                  "  if (enable_precompiled_headers) {\n    if (false) {"
                                  )
        tools.files.replace_in_file(self, os.path.join(self.source_folder, "qt5", "qtbase", "configure.json"),
                                  "-ldbus-1d",
                                  "-ldbus-1"
                                  )

    def _make_program(self):
        if self._is_msvc:
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
            return {
                "Visual Studio": "win32-msvc",
                "msvc": "win32-msvc",
                "gcc": "win32-g++",
                "clang": "win32-clang-g++",
            }.get(str(self.settings.compiler))

        elif self.settings.os == "WindowsStore":
            if self._is_msvc:
                if self.settings.compiler == "Visual Studio":
                    msvc_version = str(self.settings.compiler.version)
                else:
                    msvc_version = {
                        "190": "14",
                        "191": "15",
                        "192": "16",
                    }.get(str(self.settings.compiler.version))
                return {
                    "14": {
                        "armv7": "winrt-arm-msvc2015",
                        "x86": "winrt-x86-msvc2015",
                        "x86_64": "winrt-x64-msvc2015",
                    },
                    "15": {
                        "armv7": "winrt-arm-msvc2017",
                        "x86": "winrt-x86-msvc2017",
                        "x86_64": "winrt-x64-msvc2017",
                    },
                    "16": {
                        "armv7": "winrt-arm-msvc2019",
                        "x86": "winrt-x86-msvc2019",
                        "x86_64": "winrt-x64-msvc2019",
                    }
                }.get(msvc_version).get(str(self.settings.arch))

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
            if self._is_msvc and "MT" in msvc_runtime_flag(self):
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
            if module in self.options and not self.options.get_safe(module):
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
            args.append("--gstreamer" if self.options.get_safe("with_gstreamer", False) else "--no-gstreamer")
            args.append("--pulseaudio" if self.options.get_safe("with_pulseaudio", False) else "--no-pulseaudio")

        if self.options.with_dbus:
            args.append("-dbus-linked")
        else:
            args.append("-no-dbus")
            
        args.append("-feature-gssapi" if self.options.get_safe("with_gssapi", False) else "-no-feature-gssapi")

        for opt, conf_arg in [
                              ("with_doubleconversion", "doubleconversion"),
                              ("with_freetype", "freetype"),
                              ("with_harfbuzz", "harfbuzz"),
                              ("with_libjpeg", "libjpeg"),
                              ("with_libpng", "libpng"),
                              ("with_sqlite3", "sqlite"),
                              ("with_md4c", "libmd4c")]:
            if self.options.get_safe(opt, False):
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
                  ("xkbcommon", "XKBCOMMON"),
                  ("md4c", "LIBMD4C")]
        for package, var in libmap:
            if package in self.deps_cpp_info.deps:
                if package == "freetype":
                    args.append("\"%s_INCDIR=%s\"" % (var, self.deps_cpp_info[package].include_paths[-1]))

                args.append("\"%s_LIBS=%s\"" % (var, " ".join(self._gather_libs(package))))

        for package in self.deps_cpp_info.deps:
            args += ["-I \"%s\"" % s for s in self.deps_cpp_info[package].include_paths]
            args += ["-D %s" % s for s in self.deps_cpp_info[package].defines]
        args.append("QMAKE_LIBDIR+=\"%s\"" % " ".join(l for package in self.deps_cpp_info.deps for l in self.deps_cpp_info[package].lib_paths))
        args.append("QMAKE_RPATHLINKDIR+=\"%s\"" % ":".join(l for package in self.deps_cpp_info.deps for l in self.deps_cpp_info[package].lib_paths))

        if "libmysqlclient" in self.deps_cpp_info.deps:
            args.append("-mysql_config \"%s\"" % os.path.join(self.deps_cpp_info["libmysqlclient"].rootpath, "bin", "mysql_config"))
        if "libpq" in self.deps_cpp_info.deps:
            args.append("-psql_config \"%s\"" % os.path.join(self.deps_cpp_info["libpq"].rootpath, "bin", "pg_config"))
        if self.settings.os == "Macos":
            args += ["-no-framework"]
            if self.settings.arch == "armv8":
                args.append('QMAKE_APPLE_DEVICE_ARCHS="arm64"')
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
                if not cross_building(self, skip_x64_x86=True):
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

        if not self._is_msvc:
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

        if self.options.qtwebengine and self.settings.os in ["Linux", "FreeBSD"]:
            args += ["-qt-webengine-ffmpeg",
                     "-system-webengine-opus",
                     "-webengine-jumbo-build 0"]

        if self.options.config:
            args.append(str(self.options.config))

        os.mkdir("build_folder")
        with tools.files.chdir(self, "build_folder"):
            with tools.vcvars(self) if self._is_msvc else tools.no_op():
                build_env = {"MAKEFLAGS": "j%d" % tools.cpu_count(self, ), "PKG_CONFIG_PATH": [self.build_folder]}
                if self.settings.os == "Windows":
                    build_env["PATH"] = [os.path.join(self.source_folder, "qt5", "gnuwin32", "bin")]

                with tools.environment_append(build_env):

                    if tools.os_info.is_macos:
                        tools.files.save(self, ".qmake.stash" , "")
                        tools.files.save(self, ".qmake.super" , "")

                    self.run("%s/qt5/configure %s" % (self.source_folder, " ".join(args)), run_environment=True)
                    if tools.os_info.is_macos:
                        tools.files.save(self, "bash_env", 'export DYLD_LIBRARY_PATH="%s"' % ":".join(RunEnvironment(self).vars["DYLD_LIBRARY_PATH"]))
                    with tools.environment_append({
                        "BASH_ENV": os.path.abspath("bash_env")
                    }) if tools.os_info.is_macos else tools.no_op():
                        self.run(self._make_program(), run_environment=True)

    @property
    def _cmake_core_extras_file(self):
        return os.path.join("lib", "cmake", "Qt5Core", "conan_qt_core_extras.cmake")

    def _cmake_qt5_private_file(self, module):
        return os.path.join("lib", "cmake", "Qt5{0}".format(module), "conan_qt_qt5_{0}private.cmake".format(module.lower()))

    def package(self):
        with tools.files.chdir(self, "build_folder"):
            self.run("%s install" % self._make_program())
        tools.files.save(self, os.path.join(self.package_folder, "bin", "qt.conf"), """[Paths]
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
                tools.files.rmdir(self, os.path.join(self.package_folder, "licenses", module))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        for mask in ["Find*.cmake", "*Config.cmake", "*-config.cmake"]:
            tools.files.rm(self, self.package_folder, mask)
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la*")
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.pdb*")
        tools.files.rm(self, os.path.join(self.package_folder, "bin"), "*.pdb")
        # "Qt5Bootstrap" is internal Qt library - removing it to avoid linking error, since it contains
        # symbols that are also in "Qt5Core.lib". It looks like there is no "Qt5Bootstrap.dll".
        for fl in glob.glob(os.path.join(self.package_folder, "lib", "*Qt5Bootstrap*")):
            os.remove(fl)

        for m in os.listdir(os.path.join(self.package_folder, "lib", "cmake")):
            module = os.path.join(self.package_folder, "lib", "cmake", m, "%sMacros.cmake" % m)
            if not os.path.isfile(module):
                tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake", m))

        extension = ""
        if self.settings.os == "Windows":
            extension = ".exe"
        v = tools.scm.Version(self, self.version)
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

        if self.settings.os == "Windows":
            filecontents += textwrap.dedent("""\
                set(Qt5Core_QTMAIN_LIBRARIES Qt5::WinMain)
                if (NOT Qt5_NO_LINK_QTMAIN)
                    set(_isExe $<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>)
                    set(_isWin32 $<BOOL:$<TARGET_PROPERTY:WIN32_EXECUTABLE>>)
                    set(_isNotExcluded $<NOT:$<BOOL:$<TARGET_PROPERTY:Qt5_NO_LINK_QTMAIN>>>)
                    set(_isPolicyNEW $<TARGET_POLICY:CMP0020>)
                    set_property(TARGET Qt5::Core APPEND PROPERTY
                        INTERFACE_LINK_LIBRARIES
                            $<$<AND:${_isExe},${_isWin32},${_isNotExcluded},${_isPolicyNEW}>:Qt5::WinMain>
                    )
                    unset(_isExe)
                    unset(_isWin32)
                    unset(_isNotExcluded)
                    unset(_isPolicyNEW)
                endif()
                """)

        filecontents += textwrap.dedent("""\
            if(NOT DEFINED QT_DEFAULT_MAJOR_VERSION)
                set(QT_DEFAULT_MAJOR_VERSION %s)
            endif()
            """ % v.major)
        filecontents += 'set(CMAKE_AUTOMOC_MACRO_NAMES "Q_OBJECT" "Q_GADGET" "Q_GADGET_EXPORT" "Q_NAMESPACE" "Q_NAMESPACE_EXPORT")\n'
        tools.files.save(self, os.path.join(self.package_folder, self._cmake_core_extras_file), filecontents)

        def _create_private_module(module, dependencies=[]):
            if "Core" not in dependencies:
                dependencies.append("Core")
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
            endif()""".format(module, self.version, dependencies_string))

            tools.files.save(self, os.path.join(self.package_folder, self._cmake_qt5_private_file(module)), contents)

        _create_private_module("Core")

        if self.options.gui:
            _create_private_module("Gui", ["CorePrivate", "Gui"])

        if self.options.widgets:
            _create_private_module("Widgets", ["CorePrivate", "Gui", "GuiPrivate"])

        if self.options.qtdeclarative:
            _create_private_module("Qml", ["CorePrivate", "Qml"])

    def package_id(self):
        del self.info.options.cross_compile
        del self.info.options.sysroot
        if self.options.multiconfiguration and self._is_msvc:
            if self.settings.compiler == "Visual Studio":
                if "MD" in self.settings.compiler.runtime:
                    self.info.settings.compiler.runtime = "MD/MDd"
                else:
                    self.info.settings.compiler.runtime = "MT/MTd"
            else:
                self.info.settings.compiler.runtime_type = "Release/Debug"

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Qt5")

        self.cpp_info.names["cmake_find_package"] = "Qt5"
        self.cpp_info.names["cmake_find_package_multi"] = "Qt5"

        build_modules = []

        libsuffix = ""
        if not self.options.multiconfiguration:
            if self.settings.build_type == "Debug":
                if self.settings.os == "Windows":
                    libsuffix = "d"
                elif tools.is_apple_os(self, self.settings.os):
                    libsuffix = "_debug"

        def _get_corrected_reqs(requires):
            reqs = []
            for r in requires:
                reqs.append(r if "::" in r else "qt%s" % r)
            return reqs

        def _create_module(module, requires=[], has_include_dir=True):
            componentname = "qt%s" % module
            assert componentname not in self.cpp_info.components, "Module %s already present in self.cpp_info.components" % module
            self.cpp_info.components[componentname].set_property("cmake_target_name", "Qt5::{}".format(module))
            self.cpp_info.components[componentname].names["cmake_find_package"] = module
            self.cpp_info.components[componentname].names["cmake_find_package_multi"] = module
            if module.endswith("Private"):
                libname = module[:-7]
            else:
                libname = module
            self.cpp_info.components[componentname].libs = ["Qt5%s%s" % (libname, libsuffix)]
            if has_include_dir:
                self.cpp_info.components[componentname].includedirs = ["include", os.path.join("include", "Qt%s" % module)]
            self.cpp_info.components[componentname].defines = ["QT_%s_LIB" % module.upper()]
            if module != "Core" and "Core" not in requires:
                requires.append("Core")
            self.cpp_info.components[componentname].requires = _get_corrected_reqs(requires)

        def _create_plugin(pluginname, libname, plugintype, requires):
            componentname = "qt%s" % pluginname
            assert componentname not in self.cpp_info.components, "Plugin %s already present in self.cpp_info.components" % pluginname
            self.cpp_info.components[componentname].set_property("cmake_target_name", "Qt5::{}".format(pluginname))
            self.cpp_info.components[componentname].names["cmake_find_package"] = pluginname
            self.cpp_info.components[componentname].names["cmake_find_package_multi"] = pluginname
            if not self.options.shared:
                self.cpp_info.components[componentname].libs = [libname + libsuffix]
            self.cpp_info.components[componentname].libdirs = [os.path.join("bin", "archdatadir", "plugins", plugintype)]
            self.cpp_info.components[componentname].includedirs = []
            if "Core" not in requires:
                requires.append("Core")
            self.cpp_info.components[componentname].requires = _get_corrected_reqs(requires)

        core_reqs = ["zlib::zlib"]
        if self.options.with_pcre2:
            core_reqs.append("pcre2::pcre2")
        if self.options.with_doubleconversion:
            core_reqs.append("double-conversion::double-conversion")
        if self.options.get_safe("with_icu", False):
            core_reqs.append("icu::icu")
        if self.options.with_zstd:
            core_reqs.append("zstd::zstd")
        if self.options.with_glib:
            core_reqs.append("glib::glib-2.0")

        _create_module("Core", core_reqs)
        if self.settings.os == "Windows":
            module = "WinMain"
            componentname = "qt%s" % module
            self.cpp_info.components[componentname].set_property("cmake_target_name", "Qt5::{}".format(module))
            self.cpp_info.components[componentname].names["cmake_find_package"] = module
            self.cpp_info.components[componentname].names["cmake_find_package_multi"] = module
            self.cpp_info.components[componentname].libs = ["qtmain%s" % libsuffix]
            self.cpp_info.components[componentname].includedirs = []
            self.cpp_info.components[componentname].defines = []

        if self.options.gui:
            gui_reqs = []
            if self.options.with_dbus:
                gui_reqs.append("DBus")
            if self.options.with_freetype:
                gui_reqs.append("freetype::freetype")
            if self.options.with_libpng:
                gui_reqs.append("libpng::libpng")
            if self.options.get_safe("with_fontconfig", False):
                gui_reqs.append("fontconfig::fontconfig")
            if self.settings.os in ["Linux", "FreeBSD"]:
                gui_reqs.extend(["xorg::xorg", "xkbcommon::xkbcommon"])
            if self.options.get_safe("opengl", "no") != "no":
                gui_reqs.append("opengl::opengl")
            if self.options.get_safe("with_vulkan", False):
                gui_reqs.append("vulkan-loader::vulkan-loader")
                if tools.is_apple_os(self, self.settings.os):
                    gui_reqs.append("moltenvk::moltenvk")
            if self.options.with_harfbuzz:
                gui_reqs.append("harfbuzz::harfbuzz")
            if self.options.with_libjpeg == "libjpeg-turbo":
                gui_reqs.append("libjpeg-turbo::libjpeg-turbo")
            if self.options.with_libjpeg == "libjpeg":
                gui_reqs.append("libjpeg::libjpeg")
            if self.options.with_md4c:
                gui_reqs.append("md4c::md4c")
            _create_module("Gui", gui_reqs)
            build_modules.append(self._cmake_qt5_private_file("Gui"))
            self.cpp_info.components["qtGui"].build_modules["cmake_find_package"].append(self._cmake_qt5_private_file("Gui"))
            self.cpp_info.components["qtGui"].build_modules["cmake_find_package_multi"].append(self._cmake_qt5_private_file("Gui"))

            event_dispatcher_reqs = ["Core", "Gui"]
            if self.options.with_glib:
                event_dispatcher_reqs.append("glib::glib")
            _create_module("EventDispatcherSupport", event_dispatcher_reqs)
            _create_module("FontDatabaseSupport", ["Core", "Gui"])
            if self.settings.os == "Windows":
                self.cpp_info.components["qtFontDatabaseSupport"].system_libs.extend(["advapi32", "ole32", "user32", "gdi32"])
            elif tools.is_apple_os(self, self.settings.os):
                self.cpp_info.components["qtFontDatabaseSupport"].frameworks.extend(["CoreFoundation", "CoreGraphics", "CoreText","Foundation"])
                self.cpp_info.components["qtFontDatabaseSupport"].frameworks.append("AppKit" if self.settings.os == "Macos" else "UIKit")
            if self.options.get_safe("with_fontconfig"):
                self.cpp_info.components["qtFontDatabaseSupport"].requires.append("fontconfig::fontconfig")
            if self.options.get_safe("with_freetype"):
                self.cpp_info.components["qtFontDatabaseSupport"].requires.append("freetype::freetype")
                
            
            _create_module("ThemeSupport", ["Core", "Gui"])
            _create_module("AccessibilitySupport", ["Core", "Gui"])
            if self.options.get_safe("with_vulkan"):
                _create_module("VulkanSupport", ["Core", "Gui"])

            if tools.is_apple_os(self, self.settings.os):
                _create_module("ClipboardSupport", ["Core", "Gui"])
                self.cpp_info.components["qtClipboardSupport"].frameworks = ["ImageIO"]
                if self.settings.os == "Macos":
                    self.cpp_info.components["qtClipboardSupport"].frameworks.append("AppKit")
                _create_module("GraphicsSupport", ["Core", "Gui"])

            if self.settings.os in ["Android", "Emscripten"]:
                _create_module("EglSupport", ["Core", "Gui"])
                
            if self.settings.os == "Windows":
                windows_reqs = ["Core", "Gui"]
                windows_reqs.extend(["EventDispatcherSupport", "FontDatabaseSupport", "ThemeSupport", "AccessibilitySupport"])
                _create_module("WindowsUIAutomationSupport", ["Core", "Gui"])
                windows_reqs.append("WindowsUIAutomationSupport")
                if self.options.get_safe("with_vulkan"):
                    windows_reqs.append("VulkanSupport")
                _create_plugin("QWindowsIntegrationPlugin", "qwindows", "platforms", windows_reqs)
                _create_plugin("QWindowsVistaStylePlugin", "qwindowsvistastyle", "styles", windows_reqs)
                self.cpp_info.components["qtQWindowsIntegrationPlugin"].system_libs = ["advapi32", "dwmapi", "gdi32", "imm32",
                    "ole32", "oleaut32", "shell32", "shlwapi", "user32", "winmm", "winspool", "wtsapi32"]
            elif self.settings.os == "Android":
                android_reqs = ["Core", "Gui", "EventDispatcherSupport", "AccessibilitySupport", "FontDatabaseSupport", "EglSupport"]
                if self.options.get_safe("with_vulkan"):
                    android_reqs.append("VulkanSupport")
                _create_plugin("QAndroidIntegrationPlugin", "qtforandroid", "platforms", android_reqs)
                self.cpp_info.components["qtQAndroidIntegrationPlugin"].system_libs = ["android", "jnigraphics"]
            elif self.settings.os == "Macos":
                cocoa_reqs = ["Core", "Gui", "ClipboardSupport", "ThemeSupport", "FontDatabaseSupport", "GraphicsSupport"]
                if self.options.get_safe("with_vulkan"):
                    cocoa_reqs.append("VulkanSupport")
                if self.options.widgets:
                    cocoa_reqs.append("PrintSupport")                    
                _create_plugin("QCocoaIntegrationPlugin", "qcocoa", "platforms", cocoa_reqs)
                _create_plugin("QMacStylePlugin", "qmacstyle", "styles", cocoa_reqs)
                self.cpp_info.components["QCocoaIntegrationPlugin"].frameworks = ["AppKit", "Carbon", "CoreServices", "CoreVideo",
                    "IOKit", "IOSurface", "Metal", "QuartzCore"]
            elif self.settings.os in ["iOS", "tvOS"]:
                _create_plugin("QIOSIntegrationPlugin", "qios", "platforms", ["ClipboardSupport", "FontDatabaseSupport", "GraphicsSupport"])
                self.cpp_info.components["QIOSIntegrationPlugin"].frameworks = ["AudioToolbox", "Foundation", "Metal",
                    "QuartzCore", "UIKit"]
            elif self.settings.os == "watchOS":
                _create_plugin("QMinimalIntegrationPlugin", "qminimal", "platforms", ["EventDispatcherSupport", "FontDatabaseSupport"])
            elif self.settings.os == "Emscripten":
                _create_plugin("QWasmIntegrationPlugin", "qwasm", "platforms", ["Core", "Gui", "EventDispatcherSupport", "FontDatabaseSupport", "EglSupport"])
            elif self.settings.os in ["Linux", "FreeBSD"]:
                service_support_reqs = ["Core", "Gui"]                
                if self.options.with_dbus:
                    service_support_reqs.append("DBus")
                _create_module("ServiceSupport", service_support_reqs)
                _create_module("EdidSupport")
                _create_module("XkbCommonSupport", ["Core", "Gui", "xkbcommon::libxkbcommon-x11"])
                xcb_qpa_reqs = ["Core", "Gui", "ServiceSupport", "ThemeSupport", "FontDatabaseSupport", "EdidSupport", "XkbCommonSupport", "xorg::xorg"]
                if self.options.with_dbus and self.options.with_atspi:
                    _create_module("LinuxAccessibilitySupport", ["Core", "DBus", "Gui", "AccessibilitySupport", "at-spi2-core::at-spi2-core"])
                    xcb_qpa_reqs.append("LinuxAccessibilitySupport")
                if self.options.get_safe("with_vulkan"):
                    xcb_qpa_reqs.append("VulkanSupport")
                _create_module("XcbQpa", xcb_qpa_reqs, has_include_dir=False)
                _create_plugin("QXcbIntegrationPlugin", "qxcb", "platforms", ["Core", "Gui", "XcbQpa"])

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
        if self.settings.os in ['Linux', 'FreeBSD'] and self.options.with_gssapi:
            networkReqs.append("krb5::krb5-gssapi")
        _create_module("Network", networkReqs)
        _create_module("Sql")
        _create_module("Test")
        if self.options.widgets:
            _create_module("Widgets", ["Gui"])
            build_modules.append(self._cmake_qt5_private_file("Widgets"))
            self.cpp_info.components["qtWidgets"].build_modules["cmake_find_package"].append(self._cmake_qt5_private_file("Widgets"))
            self.cpp_info.components["qtWidgets"].build_modules["cmake_find_package_multi"].append(self._cmake_qt5_private_file("Widgets"))
        if self.options.gui and self.options.widgets:
            _create_module("PrintSupport", ["Gui", "Widgets"])
        if self.options.get_safe("opengl", "no") != "no" and self.options.gui:
            _create_module("OpenGL", ["Gui"])
        if self.options.widgets and self.options.get_safe("opengl", "no") != "no":
            _create_module("OpenGLExtensions", ["Gui"])
        if self.options.with_dbus:
            _create_module("DBus", ["dbus::dbus"])
        _create_module("Concurrent")
        _create_module("Xml")

        if self.options.qtdeclarative:
            _create_module("Qml", ["Network"])
            build_modules.append(self._cmake_qt5_private_file("Qml"))
            self.cpp_info.components["qtQml"].build_modules["cmake_find_package"].append(self._cmake_qt5_private_file("Qml"))
            self.cpp_info.components["qtQml"].build_modules["cmake_find_package_multi"].append(self._cmake_qt5_private_file("Qml"))
            _create_module("QmlModels", ["Qml"])
            self.cpp_info.components["qtQmlImportScanner"].set_property("cmake_target_name", "Qt5::QmlImportScanner")
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
            self.cpp_info.components["qtLinguistTools"].set_property("cmake_target_name", "Qt5::LinguistTools")
            self.cpp_info.components["qtLinguistTools"].names["cmake_find_package"] = "LinguistTools"
            self.cpp_info.components["qtLinguistTools"].names["cmake_find_package_multi"] = "LinguistTools"
            _create_module("UiPlugin", ["Gui", "Widgets"])
            self.cpp_info.components["qtUiPlugin"].libs = [] # this is a collection of abstract classes, so this is header-only
            self.cpp_info.components["qtUiPlugin"].libdirs = []
            _create_module("UiTools", ["UiPlugin", "Gui", "Widgets"])
            _create_module("Designer", ["Gui", "UiPlugin", "Widgets", "Xml"])
            _create_module("Help", ["Gui", "Sql", "Widgets"])

        if self.options.qtquick3d and self.options.gui:
            _create_module("Quick3DUtils", ["Gui"])
            _create_module("Quick3DAssetImport", ["Gui", "Qml", "Quick3DRender", "Quick3DUtils"])
            _create_module("Quick3DRender", ["Quick3DUtils", "Quick"])
            _create_module("Quick3DRuntimeRender", ["Quick3DRender", "Quick3DAssetImport", "Quick3DUtils"])
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
            webenginereqs = ["Gui", "Quick", "WebChannel", "Positioning"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                webenginereqs.extend(["expat::expat", "opus::libopus", "xorg-proto::xorg-proto", "libxshmfence::libxshmfence", \
                                      "nss::nss", "libdrm::libdrm"])
            _create_module("WebEngineCore", webenginereqs)
            if self.settings.os != "Windows":
                self.cpp_info.components["WebEngineCore"].system_libs.append("resolv")
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
            _create_module("3DInput", ["3DCore", "Gamepad", "Gui"])
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
            if self.options.get_safe("with_pulseaudio", False):
                multimedia_reqs.append("pulseaudio::pulse")
            _create_module("Multimedia", multimedia_reqs)
            _create_module("MultimediaWidgets", ["Multimedia", "Widgets", "Gui"])
            if self.options.qtdeclarative and self.options.gui:
                _create_module("MultimediaQuick", ["Multimedia", "Quick"])
            _create_plugin("QM3uPlaylistPlugin", "qtmultimedia_m3u", "playlistformats", [])
            if self.options.with_gstreamer:
                _create_module("MultimediaGstTools", ["Multimedia", "MultimediaWidgets", "Gui", "gst-plugins-base::gst-plugins-base"])
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

        if self.options.qtmacextras:
            _create_module("MacExtras")

        if self.options.qtxmlpatterns:
            _create_module("XmlPatterns", ["Network"])

        if self.options.qtactiveqt:
            _create_module("AxBase", ["Gui", "Widgets"])
            self.cpp_info.components["qtAxBase"].includedirs = ["include", os.path.join("include", "ActiveQt")]
            self.cpp_info.components["qtAxBase"].system_libs.extend(["ole32", "oleaut32", "user32", "gdi32", "advapi32"])
            if self.settings.compiler == "gcc":
                self.cpp_info.components["qtAxBase"].system_libs.append("uuid")
            _create_module("AxContainer", ["Core", "Gui", "Widgets", "AxBase"])
            self.cpp_info.components["qtAxContainer"].includedirs = [os.path.join("include", "ActiveQt")]
            _create_module("AxServer", ["Core", "Gui", "Widgets", "AxBase"])
            self.cpp_info.components["qtAxServer"].includedirs = [os.path.join("include", "ActiveQt")]
            self.cpp_info.components["qtAxServer"].system_libs.append("shell32")

        if self.options.qtscript:
            _create_module("Script")
            if self.options.widgets:
                _create_module("ScriptTools", ["Gui", "Widgets", "Script"])

        if self.options.qtandroidextras:
            _create_module("AndroidExtras")

        if self.options.qtwebview:
            _create_module("WebView", ["Gui", "Quick"])

        if self.options.qtvirtualkeyboard:
            _create_module("VirtualKeyboard", ["Qml", "Quick", "Gui"])

        if self.options.qtspeech:
            _create_module("TextToSpeech")

        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.components["qtCore"].system_libs.append("version")  # qtcore requires "GetFileVersionInfoW" and "VerQueryValueW" which are in "Version.lib" library
                self.cpp_info.components["qtCore"].system_libs.append("winmm")    # qtcore requires "__imp_timeSetEvent" which is in "Winmm.lib" library
                self.cpp_info.components["qtCore"].system_libs.append("netapi32") # qtcore requires "NetApiBufferFree" which is in "Netapi32.lib" library
                self.cpp_info.components["qtCore"].system_libs.append("userenv")  # qtcore requires "__imp_GetUserProfileDirectoryW " which is in "UserEnv.Lib" library
                self.cpp_info.components["qtCore"].system_libs.append("ws2_32")  # qtcore requires "WSAStartup " which is in "Ws2_32.Lib" library
                self.cpp_info.components["qtNetwork"].system_libs.append("dnsapi")  # qtnetwork from qtbase requires "DnsFree" which is in "Dnsapi.lib" library
                self.cpp_info.components["qtNetwork"].system_libs.append("iphlpapi")
                if self.options.widgets:
                    self.cpp_info.components["qtWidgets"].system_libs.append("UxTheme")
                    self.cpp_info.components["qtWidgets"].system_libs.append("dwmapi")
                if self.options.qtwinextras:
                    self.cpp_info.components["qtWinExtras"].system_libs.append("dwmapi")  # qtwinextras requires "DwmGetColorizationColor" which is in "dwmapi.lib" library


            if self.settings.os == "Macos":
                self.cpp_info.components["qtCore"].frameworks.append("IOKit")     # qtcore requires "_IORegistryEntryCreateCFProperty", "_IOServiceGetMatchingService" and much more which are in "IOKit" framework
                self.cpp_info.components["qtCore"].frameworks.append("Cocoa")     # qtcore requires "_OBJC_CLASS_$_NSApplication" and more, which are in "Cocoa" framework
                self.cpp_info.components["qtCore"].frameworks.append("Security")  # qtcore requires "_SecRequirementCreateWithString" and more, which are in "Security" framework
                self.cpp_info.components["qtNetwork"].frameworks.append("SystemConfiguration")
                if self.options.with_gssapi:
                    self.cpp_info.components["qtNetwork"].frameworks.append("GSS")

        self.cpp_info.components["qtCore"].builddirs.append(os.path.join("bin","archdatadir","bin"))
        build_modules.append(self._cmake_core_extras_file)
        self.cpp_info.components["qtCore"].build_modules["cmake_find_package"].append(self._cmake_core_extras_file)
        self.cpp_info.components["qtCore"].build_modules["cmake_find_package_multi"].append(self._cmake_core_extras_file)
        build_modules.append(self._cmake_qt5_private_file("Core"))
        self.cpp_info.components["qtCore"].build_modules["cmake_find_package"].append(self._cmake_qt5_private_file("Core"))
        self.cpp_info.components["qtCore"].build_modules["cmake_find_package_multi"].append(self._cmake_qt5_private_file("Core"))

        for m in os.listdir(os.path.join("lib", "cmake")):
            module = os.path.join("lib", "cmake", m, "%sMacros.cmake" % m)
            component_name = m.replace("Qt5", "qt")
            if os.path.isfile(module):
                build_modules.append(module)
                self.cpp_info.components[component_name].build_modules["cmake_find_package"].append(module)
                self.cpp_info.components[component_name].build_modules["cmake_find_package_multi"].append(module)
            self.cpp_info.components[component_name].builddirs.append(os.path.join("lib", "cmake", m))

        qt5core_config_extras_mkspec_dir_cmake = tools.files.load(self, 
            os.path.join("lib", "cmake", "Qt5Core", "Qt5CoreConfigExtrasMkspecDir.cmake"))
        mkspecs_dir_begin = qt5core_config_extras_mkspec_dir_cmake.find("mkspecs/")
        mkspecs_dir_end = qt5core_config_extras_mkspec_dir_cmake.find("\"", mkspecs_dir_begin)
        mkspecs_dir = qt5core_config_extras_mkspec_dir_cmake[mkspecs_dir_begin:mkspecs_dir_end].split('/')
        mkspecs_path = os.path.join("bin", "archdatadir", *mkspecs_dir)
        assert os.path.exists(mkspecs_path)
        self.cpp_info.components["qtCore"].includedirs.append(mkspecs_path)

        objects_dirs = glob.glob(os.path.join(self.package_folder, "lib", "objects-*/"))
        for object_dir in objects_dirs:
            for m in os.listdir(object_dir):
                component = "qt" + m[:m.find("_")]
                if component not in self.cpp_info.components:
                    continue
                submodules_dir = os.path.join(object_dir, m)
                for sub_dir in os.listdir(submodules_dir):
                    submodule_dir = os.path.join(submodules_dir, sub_dir)
                    obj_files = [os.path.join(submodule_dir, file) for file in os.listdir(submodule_dir)]
                    self.cpp_info.components[component].exelinkflags.extend(obj_files)
                    self.cpp_info.components[component].sharedlinkflags.extend(obj_files)

        self.cpp_info.set_property("cmake_build_modules", build_modules)

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
        if tools.is_apple_os(self, self.settings.os):
            libs += ["-framework " + i for i in self.deps_cpp_info[p].frameworks]
        libs += self.deps_cpp_info[p].sharedlinkflags
        for dep in self.deps_cpp_info[p].public_deps:
            libs += self._gather_libs(dep)
        return self._remove_duplicate(libs)
