from contextlib import contextmanager

import configparser
import functools
import glob
import os
import textwrap

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.microsoft import msvc_runtime_flag
from conans import tools, RunEnvironment, CMake
from conan.errors import ConanInvalidConfiguration
from conans.model import Generator

required_conan_version = ">=1.43.0"


class qt(Generator):
    @staticmethod
    def content_template(path, folder, os_):
        return textwrap.dedent("""\
            [Paths]
            Prefix = {0}
            ArchData = {1}/archdatadir
            HostData = {1}/archdatadir
            Data = {1}/datadir
            Sysconf = {1}/sysconfdir
            LibraryExecutables = {1}/archdatadir/{2}
            HostLibraryExecutables = bin
            Plugins = {1}/archdatadir/plugins
            Imports = {1}/archdatadir/imports
            Qml2Imports = {1}/archdatadir/qml
            Translations = {1}/datadir/translations
            Documentation = {1}/datadir/doc
            Examples = {1}/datadir/examples""").format(path, folder,
                "bin" if os_ == "Windows" else "libexec")

    @property
    def filename(self):
        return "qt.conf"

    @property
    def content(self):
        return qt.content_template(
            self.conanfile.deps_cpp_info["qt"].rootpath.replace("\\", "/"),
            "res",
            self.conanfile.settings.os)


class QtConan(ConanFile):
    _submodules = ["qtsvg", "qtdeclarative", "qttools", "qttranslations", "qtdoc",
                   "qtwayland","qtquickcontrols2", "qtquicktimeline", "qtquick3d", "qtshadertools", "qt5compat",
                   "qtactiveqt", "qtcharts", "qtdatavis3d", "qtlottie", "qtscxml", "qtvirtualkeyboard",
                   "qt3d", "qtimageformats", "qtnetworkauth", "qtcoap", "qtmqtt", "qtopcua",
                   "qtmultimedia", "qtlocation", "qtsensors", "qtconnectivity", "qtserialbus",
                   "qtserialport", "qtwebsockets", "qtwebchannel", "qtwebengine", "qtwebview",
                   "qtremoteobjects", "qtpositioning", "qtlanguageserver"]

    generators = "pkg_config", "cmake_find_package", "cmake"
    name = "qt"
    description = "Qt is a cross-platform framework for graphical user interfaces."
    topics = ("qt", "ui")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.qt.io"
    license = "LGPL-3.0"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "opengl": ["no", "desktop", "dynamic"],
        "with_vulkan": [True, False],
        "openssl": [True, False],
        "with_pcre2": [True, False],
        "with_glib": [True, False],
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
        "with_zstd": [True, False],
        "with_brotli": [True, False],
        "with_dbus": [True, False],
        "with_libalsa": [True, False],
        "with_openal": [True, False],
        "with_gstreamer": [True, False],
        "with_pulseaudio": [True, False],
        "with_gssapi": [True, False],
        "with_md4c": [True, False],

        "gui": [True, False],
        "widgets": [True, False],

        "device": "ANY",
        "cross_compile": "ANY",
        "sysroot": "ANY",
        "multiconfiguration": [True, False],
        "disabled_features": "ANY",
    }
    options.update({module: [True, False] for module in _submodules})

    # this significantly speeds up windows builds
    no_copy_source = True

    default_options = {
        "shared": False,
        "opengl": "desktop",
        "with_vulkan": False,
        "openssl": True,
        "with_pcre2": True,
        "with_glib": False,
        "with_doubleconversion": True,
        "with_freetype": True,
        "with_fontconfig": True,
        "with_icu": True,
        "with_harfbuzz": True,
        "with_libjpeg": False,
        "with_libpng": True,
        "with_sqlite3": True,
        "with_mysql": False,
        "with_pq": True,
        "with_odbc": True,
        "with_zstd": False,
        "with_brotli": True,
        "with_dbus": False,
        "with_libalsa": False,
        "with_openal": True,
        "with_gstreamer": False,
        "with_pulseaudio": False,
        "with_gssapi": False,
        "with_md4c": True,

        "gui": True,
        "widgets": True,

        "device": None,
        "cross_compile": None,
        "sysroot": None,
        "multiconfiguration": False,
        "disabled_features": "",
    }
    default_options.update({module: False for module in _submodules})

    short_paths = True

    _submodules_tree = None

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _get_module_tree(self):
        if self._submodules_tree:
            return self._submodules_tree
        config = configparser.ConfigParser()
        config.read(os.path.join(self.recipe_folder, "qtmodules%s.conf" % self.version))
        self._submodules_tree = {}
        assert config.sections()
        for s in config.sections():
            section = str(s)
            assert section.startswith("submodule ")
            assert section.count('"') == 2
            modulename = section[section.find('"') + 1: section.rfind('"')]
            status = str(config.get(section, "status"))
            if status not in ["obsolete", "ignore", "additionalLibrary"]:
                self._submodules_tree[modulename] = {"status": status,
                                "path": str(config.get(section, "path")), "depends": []}
                if config.has_option(section, "depends"):
                    self._submodules_tree[modulename]["depends"] = [str(i) for i in config.get(section, "depends").split()]

        for m in self._submodules_tree:
            assert m in ["qtbase", "qtqa", "qtrepotools"] or m in self._submodules, "module %s not in self._submodules" % m

        return self._submodules_tree

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def export(self):
        self.copy("qtmodules%s.conf" % self.version)

    def config_options(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_icu
            del self.options.with_fontconfig
            self.options.with_glib = False
            del self.options.with_libalsa

        if self.settings.os == "Windows":
            self.options.opengl = "dynamic"
            del self.options.with_gssapi
        if self.settings.os != "Linux":
            self.options.qtwayland = False

        for m in self._submodules:
            if m not in self._get_module_tree:
                delattr(self.options, m)

    @property
    def _minimum_compilers_version(self):
        # Qt6 requires C++17
        return {
            "Visual Studio": "16",
            "gcc": "8",
            "clang": "9",
            "apple-clang": "11"
        }

    def configure(self):
        if not self.options.gui:
            del self.options.opengl
            del self.options.with_vulkan
            del self.options.with_freetype
            del self.options.with_fontconfig
            del self.options.with_harfbuzz
            del self.options.with_libjpeg
            del self.options.with_libpng
            del self.options.with_md4c

        if not self.options.get_safe("qtmultimedia"):
            del self.options.with_libalsa
            del self.options.with_openal
            del self.options.with_gstreamer
            del self.options.with_pulseaudio

        if self.settings.os in ("FreeBSD", "Linux"):
            if self.options.get_safe("qtwebengine"):
                self.options.with_fontconfig = True

        if self.options.multiconfiguration:
            del self.settings.build_type

        def _enablemodule(mod):
            if mod != "qtbase":
                setattr(self.options, mod, True)
            for req in self._get_module_tree[mod]["depends"]:
                _enablemodule(req)

        for module in self._get_module_tree:
            if self.options.get_safe(module):
                _enablemodule(module)

    def validate(self):
        # C++ minimum standard required
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("C++17 support required. Your compiler is unknown. Assuming it supports C++17.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("C++17 support required, which your compiler does not support.")

        if tools.Version(self.version) >= "6.3.0" and self.settings.compiler == "clang" and "libstdc++" in str(self.settings.compiler.libcxx):
            raise ConanInvalidConfiguration("Qt needs recent libstdc++, with charconv. please switch to gcc, of to libc++")

        if self.options.get_safe("qtwebengine"):
            if not self.options.shared:
                raise ConanInvalidConfiguration("Static builds of Qt WebEngine are not supported")

            if not (self.options.gui and self.options.qtdeclarative and self.options.qtwebchannel):
                raise ConanInvalidConfiguration("option qt:qtwebengine requires also qt:gui, qt:qtdeclarative and qt:qtwebchannel")

            if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
                raise ConanInvalidConfiguration("Cross compiling Qt WebEngine is not supported")

            if tools.Version(self.version) < "6.3.0":
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
                if v_min <= version < v_max:
                    msg = ("Found valid Python 2 required for QtWebengine:"
                           " version={}, path={}".format(mybuf.getvalue(), python_exe))
                    self.output.success(msg)
                else:
                    msg = ("Found Python 2 in path, but with invalid version {}"
                           " (QtWebEngine requires >= {} & < "
                           "{})\nIf you have both Python 2 and 3 installed, copy the python 2 executable to"
                           "python2(.exe)".format(verstr, v_min, v_max))
                    raise ConanInvalidConfiguration(msg)

        if self.options.widgets and not self.options.gui:
            raise ConanInvalidConfiguration("using option qt:widgets without option qt:gui is not possible. "
                                            "You can either disable qt:widgets or enable qt:gui")
        if self.settings.os == "Android" and self.options.get_safe("opengl", "no") == "desktop":
            raise ConanInvalidConfiguration("OpenGL desktop is not supported on Android.")

        if self.settings.os != "Windows" and self.options.get_safe("opengl", "no") == "dynamic":
            raise ConanInvalidConfiguration("Dynamic OpenGL is supported only on Windows.")

        if self.options.get_safe("with_fontconfig", False) and not self.options.get_safe("with_freetype", False):
            raise ConanInvalidConfiguration("with_fontconfig cannot be enabled if with_freetype is disabled.")

        if "MT" in self.settings.get_safe("compiler.runtime", default="") and self.options.shared:
            raise ConanInvalidConfiguration("Qt cannot be built as shared library with static runtime")

        if self.options.get_safe("with_pulseaudio", False) or self.options.get_safe("with_libalsa", False):
            raise ConanInvalidConfiguration("alsa and pulseaudio are not supported (QTBUG-95116), please disable them.")
        if not self.options.with_pcre2:
            raise ConanInvalidConfiguration("pcre2 is actually required by qt (QTBUG-92454). please use option qt:with_pcre2=True")

        if self.settings.os in ['Linux', 'FreeBSD'] and self.options.with_gssapi:
            raise ConanInvalidConfiguration("gssapi cannot be enabled until conan-io/conan-center-index#4102 is closed")

    def requirements(self):
        self.requires("zlib/1.2.12")
        if self.options.openssl:
            self.requires("openssl/1.1.1q")
        if self.options.with_pcre2:
            self.requires("pcre2/10.37") # needs to be < 10.38 or qt fails to detect visual studio static library
        if self.options.get_safe("with_vulkan"):
            self.requires("vulkan-loader/1.3.221.0")
            if tools.is_apple_os(self.settings.os):
                self.requires("moltenvk/1.1.10")
        if self.options.with_glib:
            self.requires("glib/2.73.2")
        if self.options.with_doubleconversion and not self.options.multiconfiguration:
            self.requires("double-conversion/3.2.0")
        if self.options.get_safe("with_freetype", False) and not self.options.multiconfiguration:
            self.requires("freetype/2.12.1")
        if self.options.get_safe("with_fontconfig", False):
            self.requires("fontconfig/2.13.93")
        if self.options.get_safe("with_icu", False):
            self.requires("icu/71.1")
        if self.options.get_safe("with_harfbuzz", False) and not self.options.multiconfiguration:
            self.requires("harfbuzz/4.4.1")
        if self.options.get_safe("with_libjpeg", False) and not self.options.multiconfiguration:
            if self.options.with_libjpeg == "libjpeg-turbo":
                self.requires("libjpeg-turbo/2.1.3")
            else:
                self.requires("libjpeg/9d")
        if self.options.get_safe("with_libpng", False) and not self.options.multiconfiguration:
            self.requires("libpng/1.6.37")
        if self.options.with_sqlite3 and not self.options.multiconfiguration:
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
            self.requires("openal/1.22.1")
        if self.options.get_safe("with_libalsa", False):
            self.requires("libalsa/1.2.7.2")
        if self.options.gui and self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system")
            self.requires("xkbcommon/1.4.1")
        if self.settings.os != "Windows" and self.options.get_safe("opengl", "no") != "no":
            self.requires("opengl/system")
        if self.options.with_zstd:
            self.requires("zstd/1.5.2")
        if self.options.qtwayland:
            self.requires("wayland/1.21.0")
        if self.options.with_brotli:
            self.requires("brotli/1.0.9")
        if self.options.get_safe("qtwebengine") and self.settings.os == "Linux":
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
        if self.settings.os in ['Linux', 'FreeBSD'] and self.options.with_gssapi:
            self.requires("krb5/1.18.3") # conan-io/conan-center-index#4102
        if self.options.get_safe("with_md4c", False):
            self.requires("md4c/0.4.8")

    def build_requirements(self):
        self.build_requires("cmake/3.23.2")
        self.build_requires("ninja/1.11.0")
        self.build_requires("pkgconf/1.7.4")
        if self.settings.os == "Windows":
            self.build_requires('strawberryperl/5.30.0.1')

        if self.options.get_safe("qtwebengine"):
            self.build_requires("nodejs/16.3.0")
            self.build_requires("gperf/3.1")
            # gperf, bison, flex, python >= 2.7.5 & < 3
            if self.settings.os != "Windows":
                self.build_requires("bison/3.7.6")
                self.build_requires("flex/2.6.4")
            else:
                self.build_requires("winflexbison/2.5.24")

        if self.options.qtwayland:
            self.build_requires("wayland/1.21.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination="qt6")

        # patching in source method because of no_copy_source attribute

        tools.files.replace_in_file(self, os.path.join("qt6", "CMakeLists.txt"),
                        "enable_testing()",
                        "include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)\nconan_basic_setup(KEEP_RPATHS)\n"
                               "set(QT_EXTRA_INCLUDEPATHS ${CONAN_INCLUDE_DIRS})\n"
                               "set(QT_EXTRA_DEFINES ${CONAN_DEFINES})\n"
                               "set(QT_EXTRA_LIBDIRS ${CONAN_LIB_DIRS})\n"
                               "enable_testing()")

        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        if tools.Version(self.version) >= "6.2.0":
            for f in ["renderer", os.path.join("renderer", "core"), os.path.join("renderer", "platform")]:
                tools.files.replace_in_file(self, os.path.join(self.source_folder, "qt6", "qtwebengine", "src", "3rdparty", "chromium", "third_party", "blink", f, "BUILD.gn"),
                                      "  if (enable_precompiled_headers) {\n    if (is_win) {",
                                      "  if (enable_precompiled_headers) {\n    if (false) {"
                                      )

        tools.files.replace_in_file(self, os.path.join("qt6", "qtbase", "cmake", "QtInternalTargets.cmake"),
                              "-Zc:wchar_t",
                              "-Zc:wchar_t -Zc:twoPhase-")
        for f in ["FindPostgreSQL.cmake"]:
            file = os.path.join("qt6", "qtbase", "cmake", f)
            if os.path.isfile(file):
                os.remove(file)

        # workaround QTBUG-94356
        if tools.Version(self.version) >= "6.1.1":
            zlib_file_name = "FindWrapSystemZLIB.cmake" if tools.Version(self.version) >= "6.3.1" else "FindWrapZLIB.cmake"
            tools.files.replace_in_file(self, os.path.join("qt6", "qtbase", "cmake", zlib_file_name), '"-lz"', 'ZLIB::ZLIB')
            tools.files.replace_in_file(self, os.path.join("qt6", "qtbase", "configure.cmake"),
                "set_property(TARGET ZLIB::ZLIB PROPERTY IMPORTED_GLOBAL TRUE)",
                "")

    def _xplatform(self):
        if self.settings.os == "Linux":
            if self.settings.compiler == "gcc":
                return {"x86": "linux-g++-32",
                        "armv6": "linux-arm-gnueabi-g++",
                        "armv7": "linux-arm-gnueabi-g++",
                        "armv7hf": "linux-arm-gnueabi-g++",
                        "armv8": "linux-aarch64-gnu-g++"}.get(str(self.settings.arch), "linux-g++")
            if self.settings.compiler == "clang":
                if self.settings.arch == "x86":
                    return "linux-clang-libc++-32" if self.settings.compiler.libcxx == "libc++" else "linux-clang-32"
                if self.settings.arch == "x86_64":
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

    @contextmanager
    def _build_context(self):
        with tools.vcvars(self) if self._is_msvc else tools.no_op():
            # next lines force cmake package to be in PATH before the one provided by visual studio (vcvars)
            build_env = tools.RunEnvironment(self).vars if self._is_msvc else {}
            build_env["MAKEFLAGS"] = "j%d" % tools.cpu_count()
            build_env["PKG_CONFIG_PATH"] = [self.build_folder]
            if self.settings.os == "Windows":
                if "PATH" not in build_env:
                    build_env["PATH"] = []
                build_env["PATH"].append(os.path.join(self.source_folder, "qt6", "gnuwin32", "bin"))
            if self._is_msvc:
                # this avoids cmake using gcc from strawberryperl
                build_env["CC"] = "cl"
                build_env["CXX"] = "cl"
            with tools.environment_append(build_env):

                if tools.os_info.is_macos:
                    tools.files.save(self, ".qmake.stash" , "")
                    tools.files.save(self, ".qmake.super" , "")
                yield

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self, generator="Ninja")

        cmake.definitions["INSTALL_MKSPECSDIR"] = os.path.join(self.package_folder, "res", "archdatadir", "mkspecs")
        cmake.definitions["INSTALL_ARCHDATADIR"] = os.path.join(self.package_folder, "res", "archdatadir")
        cmake.definitions["INSTALL_LIBEXECDIR"] = os.path.join(self.package_folder, "bin")
        cmake.definitions["INSTALL_DATADIR"] = os.path.join(self.package_folder, "res", "datadir")
        cmake.definitions["INSTALL_SYSCONFDIR"] = os.path.join(self.package_folder, "res", "sysconfdir")

        cmake.definitions["QT_BUILD_TESTS"] = "OFF"
        cmake.definitions["QT_BUILD_EXAMPLES"] = "OFF"

        if self._is_msvc and "MT" in msvc_runtime_flag(self):
            cmake.definitions["FEATURE_static_runtime"] = "ON"

        if self.options.multiconfiguration:
            cmake.generator = "Ninja Multi-Config"
            cmake.definitions["CMAKE_CONFIGURATION_TYPES"] = "Release;Debug"
        cmake.definitions["FEATURE_optimize_size"] = ("ON" if self.settings.build_type == "MinSizeRel" else "OFF")

        for module in self._get_module_tree:
            if module != 'qtbase':
                cmake.definitions["BUILD_%s" % module] = ("ON" if self.options.get_safe(module) else "OFF")

        cmake.definitions["FEATURE_system_zlib"] = "ON"

        cmake.definitions["INPUT_opengl"] = self.options.get_safe("opengl", "no")

        # openSSL
        if not self.options.openssl:
            cmake.definitions["INPUT_openssl"] = "no"
        else:
            if self.options["openssl"].shared:
                cmake.definitions["INPUT_openssl"] = "runtime"
            else:
                cmake.definitions["INPUT_openssl"] = "linked"

        if self.options.with_dbus:
            cmake.definitions["INPUT_dbus"] = "linked"
        else:
            cmake.definitions["FEATURE_dbus"] = "OFF"


        for opt, conf_arg in [("with_glib", "glib"),
                              ("with_icu", "icu"),
                              ("with_fontconfig", "fontconfig"),
                              ("with_mysql", "sql_mysql"),
                              ("with_pq", "sql_psql"),
                              ("with_odbc", "sql_odbc"),
                              ("gui", "gui"),
                              ("widgets", "widgets"),
                              ("with_zstd", "zstd"),
                              ("with_vulkan", "vulkan"),
                              ("with_brotli", "brotli"),
                              ("with_gssapi", "gssapi")]:
            cmake.definitions["FEATURE_%s" % conf_arg] = ("ON" if self.options.get_safe(opt, False) else "OFF")


        for opt, conf_arg in [
                              ("with_doubleconversion", "doubleconversion"),
                              ("with_freetype", "freetype"),
                              ("with_harfbuzz", "harfbuzz"),
                              ("with_libjpeg", "jpeg"),
                              ("with_libpng", "png"),
                              ("with_sqlite3", "sqlite"),
                              ("with_pcre2", "pcre2"),]:
            if self.options.get_safe(opt, False):
                if self.options.multiconfiguration:
                    cmake.definitions["FEATURE_%s" % conf_arg] = "ON"
                else:
                    cmake.definitions["FEATURE_system_%s" % conf_arg] = "ON"
            else:
                cmake.definitions["FEATURE_%s" % conf_arg] = "OFF"
                cmake.definitions["FEATURE_system_%s" % conf_arg] = "OFF"

        for opt, conf_arg in [
                              ("with_doubleconversion", "doubleconversion"),
                              ("with_freetype", "freetype"),
                              ("with_harfbuzz", "harfbuzz"),
                              ("with_libjpeg", "libjpeg"),
                              ("with_libpng", "libpng"),
                              ("with_md4c", "libmd4c"),
                              ("with_pcre2", "pcre"),]:
            if self.options.get_safe(opt, False):
                if self.options.multiconfiguration:
                    cmake.definitions["INPUT_%s" % conf_arg] = "qt"
                else:
                    cmake.definitions["INPUT_%s" % conf_arg] = "system"
            else:
                cmake.definitions["INPUT_%s" % conf_arg] = "no"

        for feature in str(self.options.disabled_features).split():
            cmake.definitions["FEATURE_%s" % feature] = "OFF"

        if self.settings.os == "Macos":
            cmake.definitions["FEATURE_framework"] = "OFF"
        elif self.settings.os == "Android":
            cmake.definitions["CMAKE_ANDROID_NATIVE_API_LEVEL"] = self.settings.os.api_level
            cmake.definitions["ANDROID_ABI"] =  {"armv7": "armeabi-v7a",
                                           "armv8": "arm64-v8a",
                                           "x86": "x86",
                                           "x86_64": "x86_64"}.get(str(self.settings.arch))

        if self.options.sysroot:
            cmake.definitions["CMAKE_SYSROOT"] = self.options.sysroot

        if self.options.device:
            cmake.definitions["QT_QMAKE_TARGET_MKSPEC"] = os.path.join("devices", self.options.device)
        else:
            xplatform_val = self._xplatform()
            if xplatform_val:
                cmake.definitions["QT_QMAKE_TARGET_MKSPEC"] = xplatform_val
            else:
                self.output.warn("host not supported: %s %s %s %s" %
                                 (self.settings.os, self.settings.compiler,
                                  self.settings.compiler.version, self.settings.arch))
        if self.options.cross_compile:
            cmake.definitions["QT_QMAKE_DEVICE_OPTIONS"] = "CROSS_COMPILE=%s" % self.options.cross_compile

        cmake.definitions["FEATURE_pkg_config"] = "ON"
        if self.settings.compiler == "gcc" and self.settings.build_type == "Debug" and not self.options.shared:
            cmake.definitions["BUILD_WITH_PCH"]= "OFF" # disabling PCH to save disk space

        if self.settings.os == "Windows":
            cmake.definitions["HOST_PERL"] = getattr(self, "user_info_build", self.deps_user_info)["strawberryperl"].perl

        try:
            cmake.configure(source_folder="qt6")
        except:
            cmake_err_log = os.path.join(self.build_folder, "CMakeFiles", "CMakeError.log")
            cmake_out_log = os.path.join(self.build_folder, "CMakeFiles", "CMakeOutput.log")
            if os.path.isfile(cmake_err_log):
                self.output.info(tools.files.load(self, cmake_err_log))
            if os.path.isfile(cmake_out_log):
                self.output.info(tools.files.load(self, cmake_out_log))
            raise
        return cmake

    def build(self):
        for f in glob.glob("*.cmake"):
            tools.files.replace_in_file(self, f,
                "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:>",
                "", strict=False)
            tools.files.replace_in_file(self, f,
                "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:>",
                "", strict=False)
            tools.files.replace_in_file(self, f,
                "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:>",
                "", strict=False)
            tools.files.replace_in_file(self, f,
                "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:-Wl,--export-dynamic>",
                "", strict=False)
            tools.files.replace_in_file(self, f,
                "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:-Wl,--export-dynamic>",
                "", strict=False)
            tools.files.replace_in_file(self, f,
                " IMPORTED)\n",
                " IMPORTED GLOBAL)\n", strict=False)

        with self._build_context():
            cmake = self._configure_cmake()
            if tools.os_info.is_macos:
                tools.files.save(self, "bash_env", 'export DYLD_LIBRARY_PATH="%s"' % ":".join(RunEnvironment(self).vars["DYLD_LIBRARY_PATH"]))
            with tools.environment_append({
                "BASH_ENV": os.path.abspath("bash_env")
            }) if tools.os_info.is_macos else tools.no_op():
                with tools.run_environment(self):
                    with tools.remove_from_path("perl") if self.settings.os == "Windows" else tools.no_op():
                        cmake.build()

    @property
    def _cmake_executables_file(self):
        return os.path.join("lib", "cmake", "Qt6Core", "conan_qt_executables_variables.cmake")

    @property
    def _cmake_entry_point_file(self):
        return os.path.join("lib", "cmake", "Qt6Core", "conan_qt_entry_point.cmake")

    def _cmake_qt6_private_file(self, module):
        return os.path.join("lib", "cmake", "Qt6{0}".format(module), "conan_qt_qt6_{0}private.cmake".format(module.lower()))

    def package(self):
        with self._build_context():
            cmake = self._configure_cmake()
            cmake.install()
        tools.files.save(self, os.path.join(self.package_folder, "bin", "qt.conf"), qt.content_template("..", "res", self.settings.os))
        self.copy("*LICENSE*", src="qt6/", dst="licenses")
        for module in self._get_module_tree:
            if module != "qtbase" and not self.options.get_safe(module):
                tools.files.rmdir(self, os.path.join(self.package_folder, "licenses", module))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        for mask in ["Find*.cmake", "*Config.cmake", "*-config.cmake"]:
            tools.files.rm(self, self.package_folder, mask)
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la*")
        tools.files.rm(self, self.package_folder, "*.pdb*")
        tools.files.rm(self, self.package_folder, "ensure_pro_file.cmake")
        os.remove(os.path.join(self.package_folder, "bin", "qt-cmake-private-install.cmake"))

        for m in os.listdir(os.path.join(self.package_folder, "lib", "cmake")):
            module = os.path.join(self.package_folder, "lib", "cmake", m, "%sMacros.cmake" % m)
            helper_modules = glob.glob(os.path.join(self.package_folder, "lib", "cmake", m, "QtPublic*Helpers.cmake"))
            if not os.path.isfile(module) and not helper_modules:
                tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake", m))

        extension = ""
        if self.settings.os == "Windows":
            extension = ".exe"
        filecontents = "set(QT_CMAKE_EXPORT_NAMESPACE Qt6)\n"
        ver = tools.Version(self.version)
        filecontents += "set(QT_VERSION_MAJOR %s)\n" % ver.major
        filecontents += "set(QT_VERSION_MINOR %s)\n" % ver.minor
        filecontents += "set(QT_VERSION_PATCH %s)\n" % ver.patch
        targets = ["moc", "rcc", "tracegen", "cmake_automoc_parser", "qlalr", "qmake"]
        if self.options.with_dbus:
            targets.extend(["qdbuscpp2xml", "qdbusxml2cpp"])
        if self.options.gui:
            targets.append("qvkgen")
        if self.options.widgets:
            targets.append("uic")
        if self.options.qttools:
            targets.extend(["qhelpgenerator", "qtattributionsscanner"])
            if self.settings.os == "Windows":
                targets.extend(["windeployqt"])
            targets.extend(["lconvert", "lprodump", "lrelease", "lrelease-pro", "lupdate", "lupdate-pro"])
        if self.options.qtshadertools:
            targets.append("qsb")
        if self.options.qtdeclarative:
            targets.extend(["qmltyperegistrar", "qmlcachegen", "qmllint", "qmlimportscanner"])
            targets.extend(["qmlformat", "qml", "qmlprofiler", "qmlpreview", "qmltestrunner"])
        if self.options.get_safe("qtremoteobjects"):
            targets.append("repc")
        for target in targets:
            exe_path = None
            for path_ in ["bin/{0}{1}".format(target, extension),
                          "lib/{0}{1}".format(target, extension)]:
                if os.path.isfile(os.path.join(self.package_folder, path_)):
                    exe_path = path_
                    break
            if not exe_path:
                self.output.warn("Could not find path to {0}{1}".format(target, extension))
            filecontents += textwrap.dedent("""\
                if(NOT TARGET ${{QT_CMAKE_EXPORT_NAMESPACE}}::{0})
                    add_executable(${{QT_CMAKE_EXPORT_NAMESPACE}}::{0} IMPORTED)
                    set_target_properties(${{QT_CMAKE_EXPORT_NAMESPACE}}::{0} PROPERTIES IMPORTED_LOCATION ${{CMAKE_CURRENT_LIST_DIR}}/../../../{1})
                endif()
                """.format(target, exe_path))

        filecontents += textwrap.dedent("""\
            if(NOT DEFINED QT_DEFAULT_MAJOR_VERSION)
                set(QT_DEFAULT_MAJOR_VERSION %s)
            endif()
            """ % ver.major)
        filecontents += 'set(CMAKE_AUTOMOC_MACRO_NAMES "Q_OBJECT" "Q_GADGET" "Q_GADGET_EXPORT" "Q_NAMESPACE" "Q_NAMESPACE_EXPORT")\n'
        tools.files.save(self, os.path.join(self.package_folder, self._cmake_executables_file), filecontents)

        def _create_private_module(module, dependencies=[]):
            dependencies_string = ';'.join('Qt6::%s' % dependency for dependency in dependencies)
            contents = textwrap.dedent("""\
            if(NOT TARGET Qt6::{0}Private)
                add_library(Qt6::{0}Private INTERFACE IMPORTED)

                set_target_properties(Qt6::{0}Private PROPERTIES
                    INTERFACE_INCLUDE_DIRECTORIES "${{CMAKE_CURRENT_LIST_DIR}}/../../../include/Qt{0}/{1};${{CMAKE_CURRENT_LIST_DIR}}/../../../include/Qt{0}/{1}/Qt{0}"
                    INTERFACE_LINK_LIBRARIES "{2}"
                )

                add_library(Qt::{0}Private INTERFACE IMPORTED)
                set_target_properties(Qt::{0}Private PROPERTIES
                    INTERFACE_LINK_LIBRARIES "Qt6::{0}Private"
                    _qt_is_versionless_target "TRUE"
                )
            endif()""".format(module, self.version, dependencies_string))

            tools.files.save(self, os.path.join(self.package_folder, self._cmake_qt6_private_file(module)), contents)

        _create_private_module("Core", ["Core"])

        if self.options.gui:
            _create_private_module("Gui", ["CorePrivate", "Gui"])

        if self.options.widgets:
            _create_private_module("Widgets", ["CorePrivate", "GuiPrivate", "Widgets"])

        if self.options.qtdeclarative:
            _create_private_module("Qml", ["CorePrivate", "Qml"])

        if self.settings.os in ["Windows", "iOS"]:
            contents = textwrap.dedent("""\
                set(entrypoint_conditions "$<NOT:$<BOOL:$<TARGET_PROPERTY:qt_no_entrypoint>>>")
                list(APPEND entrypoint_conditions "$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>")
                if(WIN32)
                    list(APPEND entrypoint_conditions "$<BOOL:$<TARGET_PROPERTY:WIN32_EXECUTABLE>>")
                endif()
                list(JOIN entrypoint_conditions "," entrypoint_conditions)
                set(entrypoint_conditions "$<AND:${entrypoint_conditions}>")
                set_property(
                    TARGET ${QT_CMAKE_EXPORT_NAMESPACE}::Core
                    APPEND PROPERTY INTERFACE_LINK_LIBRARIES "$<${entrypoint_conditions}:${QT_CMAKE_EXPORT_NAMESPACE}::EntryPointPrivate>"
                )""")
            tools.files.save(self, os.path.join(self.package_folder, self._cmake_entry_point_file), contents)

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
        self.cpp_info.set_property("cmake_file_name", "Qt6")

        self.cpp_info.names["cmake_find_package"] = "Qt6"
        self.cpp_info.names["cmake_find_package_multi"] = "Qt6"

        # consumers will need the QT_PLUGIN_PATH defined in runenv
        self.runenv_info.define("QT_PLUGIN_PATH", os.path.join(self.package_folder, "res", "archdatadir", "plugins"))
        self.buildenv_info.define("QT_PLUGIN_PATH", os.path.join(self.package_folder, "res", "archdatadir", "plugins"))

        build_modules = []

        libsuffix = ""
        if self.settings.build_type == "Debug":
            if self.settings.os == "Windows":
                libsuffix = "d"
            if tools.is_apple_os(self.settings.os):
                libsuffix = "_debug"

        def _get_corrected_reqs(requires):
            reqs = []
            for r in requires:
                reqs.append(r if "::" in r else "qt%s" % r)
            return reqs

        def _create_module(module, requires=[], has_include_dir=True):
            componentname = "qt%s" % module
            assert componentname not in self.cpp_info.components, "Module %s already present in self.cpp_info.components" % module
            self.cpp_info.components[componentname].set_property("cmake_target_name", "Qt6::{}".format(module))
            self.cpp_info.components[componentname].names["cmake_find_package"] = module
            self.cpp_info.components[componentname].names["cmake_find_package_multi"] = module
            if module.endswith("Private"):
                libname = module[:-7]
            else:
                libname = module
            self.cpp_info.components[componentname].libs = ["Qt6%s%s" % (libname, libsuffix)]
            if has_include_dir:
                self.cpp_info.components[componentname].includedirs = ["include", os.path.join("include", "Qt%s" % module)]
            self.cpp_info.components[componentname].defines = ["QT_%s_LIB" % module.upper()]
            if module != "Core" and "Core" not in requires:
                requires.append("Core")
            self.cpp_info.components[componentname].requires = _get_corrected_reqs(requires)

        def _create_plugin(pluginname, libname, type, requires):
            componentname = "qt%s" % pluginname
            assert componentname not in self.cpp_info.components, "Plugin %s already present in self.cpp_info.components" % pluginname
            self.cpp_info.components[componentname].set_property("cmake_target_name", "Qt6::{}".format(pluginname))
            self.cpp_info.components[componentname].names["cmake_find_package"] = pluginname
            self.cpp_info.components[componentname].names["cmake_find_package_multi"] = pluginname
            if not self.options.shared:
                self.cpp_info.components[componentname].libs = [libname + libsuffix]
            self.cpp_info.components[componentname].libdirs = [os.path.join("res", "archdatadir", "plugins", type)]
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
            core_reqs.append("glib::glib")

        _create_module("Core", core_reqs)
        if self.settings.os == "Windows":
            if tools.Version(self.version) >= "6.3.0":
                self.cpp_info.components["qtCore"].system_libs.append("authz")
        if self._is_msvc:
            if tools.Version(self.version) >= "6.3.0":
                self.cpp_info.components["qtCore"].cxxflags.append("-permissive-")
            if tools.Version(self.version) >= "6.2.0":
                self.cpp_info.components["qtCore"].cxxflags.append("-Zc:__cplusplus")
                self.cpp_info.components["qtCore"].system_libs.append("synchronization")
            if tools.Version(self.version) >= "6.2.1":
                self.cpp_info.components["qtCore"].system_libs.append("runtimeobject")
        self.cpp_info.components["qtPlatform"].set_property("cmake_target_name", "Qt6::Platform")
        self.cpp_info.components["qtPlatform"].names["cmake_find_package"] = "Platform"
        self.cpp_info.components["qtPlatform"].names["cmake_find_package_multi"] = "Platform"
        self.cpp_info.components["qtPlatform"].includedirs = [os.path.join("res", "archdatadir", "mkspecs", self._xplatform())]
        if tools.Version(self.version) < "6.1.0":
            self.cpp_info.components["qtCore"].libs.append("Qt6Core_qobject%s" % libsuffix)
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
            if self.settings.os != "Windows" and self.options.get_safe("opengl", "no") != "no":
                gui_reqs.append("opengl::opengl")
            if self.options.get_safe("with_vulkan", False):
                gui_reqs.append("vulkan-loader::vulkan-loader")
                if tools.is_apple_os(self.settings.os):
                    gui_reqs.append("moltenvk::moltenvk")
            if self.options.with_harfbuzz:
                gui_reqs.append("harfbuzz::harfbuzz")
            if self.options.with_glib:
                gui_reqs.append("glib::glib")
            if self.options.with_md4c:
                gui_reqs.append("md4c::md4c")
            _create_module("Gui", gui_reqs)

            build_modules.append(self._cmake_qt6_private_file("Gui"))
            self.cpp_info.components["qtGui"].build_modules["cmake_find_package"].append(self._cmake_qt6_private_file("Gui"))
            self.cpp_info.components["qtGui"].build_modules["cmake_find_package_multi"].append(self._cmake_qt6_private_file("Gui"))

            if self.settings.os == "Windows":
                _create_plugin("QWindowsIntegrationPlugin", "qwindows", "platforms", ["Core", "Gui"])
                _create_plugin("QWindowsVistaStylePlugin", "qwindowsvistastyle", "styles", ["Core", "Gui"])
                self.cpp_info.components["qtQWindowsIntegrationPlugin"].system_libs = ["advapi32", "dwmapi", "gdi32", "imm32",
                    "ole32", "oleaut32", "shell32", "shlwapi", "user32", "winmm", "winspool", "wtsapi32"]
            elif self.settings.os == "Android":
                _create_plugin("QAndroidIntegrationPlugin", "qtforandroid", "platforms", ["Core", "Gui"])
                self.cpp_info.components["qtQAndroidIntegrationPlugin"].system_libs = ["android", "jnigraphics"]
            elif self.settings.os == "Macos":
                _create_plugin("QCocoaIntegrationPlugin", "qcocoa", "platforms", ["Core", "Gui"])
                self.cpp_info.components["QCocoaIntegrationPlugin"].frameworks = ["AppKit", "Carbon", "CoreServices", "CoreVideo",
                    "IOKit", "IOSurface", "Metal", "QuartzCore"]
            elif self.settings.os in ["iOS", "tvOS"]:
                _create_plugin("QIOSIntegrationPlugin", "qios", "platforms", [])
                self.cpp_info.components["QIOSIntegrationPlugin"].frameworks = ["AudioToolbox", "Foundation", "Metal",
                    "QuartzCore", "UIKit"]
            elif self.settings.os == "watchOS":
                _create_plugin("QMinimalIntegrationPlugin", "qminimal", "platforms", [])
            elif self.settings.os == "Emscripten":
                _create_plugin("QWasmIntegrationPlugin", "qwasm", "platforms", ["Core", "Gui"])
            elif self.settings.os in ["Linux", "FreeBSD"]:
                _create_module("XcbQpaPrivate", ["xkbcommon::libxkbcommon-x11", "xorg::xorg"], has_include_dir=False)
                _create_plugin("QXcbIntegrationPlugin", "qxcb", "platforms", ["Core", "Gui", "XcbQpaPrivate"])

            _create_plugin("QGifPlugin", "qgif", "imageformats", ["Gui"])
            _create_plugin("QIcoPlugin", "qico", "imageformats", ["Gui"])
            if self.options.get_safe("with_libjpeg"):
                jpeg_reqs = ["Gui"]
                if self.options.with_libjpeg == "libjpeg-turbo": 
                     jpeg_reqs.append("libjpeg-turbo::libjpeg-turbo") 
                if self.options.with_libjpeg == "libjpeg": 
                     jpeg_reqs.append("libjpeg::libjpeg") 
                _create_plugin("QJpegPlugin", "qjpeg", "imageformats", jpeg_reqs)

        if self.options.with_sqlite3:
            _create_plugin("QSQLiteDriverPlugin", "qsqlite", "sqldrivers", ["sqlite3::sqlite3"])
        if self.options.with_pq:
            _create_plugin("QPSQLDriverPlugin", "qsqlpsql", "sqldrivers", ["libpq::libpq"])
        if self.options.with_odbc:
            if self.settings.os != "Windows":
                _create_plugin("QODBCDriverPlugin", "qsqlodbc", "sqldrivers", ["odbc::odbc"])
        networkReqs = []
        if self.options.openssl:
            networkReqs.append("openssl::openssl")
        if self.options.with_brotli:
            networkReqs.append("brotli::brotli")
        if self.settings.os in ['Linux', 'FreeBSD'] and self.options.with_gssapi:
            networkReqs.append("krb5::krb5-gssapi")
        _create_module("Network", networkReqs)
        _create_module("Sql")
        _create_module("Test")
        if self.options.widgets:
            _create_module("Widgets", ["Gui"])
            build_modules.append(self._cmake_qt6_private_file("Widgets"))
            self.cpp_info.components["qtWidgets"].build_modules["cmake_find_package"].append(self._cmake_qt6_private_file("Widgets"))
            self.cpp_info.components["qtWidgets"].build_modules["cmake_find_package_multi"].append(self._cmake_qt6_private_file("Widgets"))
        if self.options.gui and self.options.widgets:
            _create_module("PrintSupport", ["Gui", "Widgets"])
        if self.options.get_safe("opengl", "no") != "no" and self.options.gui:
            _create_module("OpenGL", ["Gui"])
        if self.options.widgets and self.options.get_safe("opengl", "no") != "no":
            _create_module("OpenGLWidgets", ["OpenGL", "Widgets"])
        if self.options.with_dbus:
            _create_module("DBus", ["dbus::dbus"])
        _create_module("Concurrent")
        _create_module("Xml")

        if self.options.qt5compat:
            _create_module("Core5Compat")

        # since https://github.com/qt/qtdeclarative/commit/4fb84137f1c0a49d64b8bef66fef8a4384cc2a68
        qt_quick_enabled = self.options.gui and (tools.Version(self.version) < "6.2.0" or self.options.qtshadertools)

        if self.options.qtdeclarative:
            _create_module("Qml", ["Network"])
            build_modules.append(self._cmake_qt6_private_file("Qml"))
            self.cpp_info.components["qtQml"].build_modules["cmake_find_package"].append(self._cmake_qt6_private_file("Qml"))
            self.cpp_info.components["qtQml"].build_modules["cmake_find_package_multi"].append(self._cmake_qt6_private_file("Qml"))
            _create_module("QmlModels", ["Qml"])
            self.cpp_info.components["qtQmlImportScanner"].set_property("cmake_target_name", "Qt6::QmlImportScanner")
            self.cpp_info.components["qtQmlImportScanner"].names["cmake_find_package"] = "QmlImportScanner" # this is an alias for Qml and there to integrate with existing consumers
            self.cpp_info.components["qtQmlImportScanner"].names["cmake_find_package_multi"] = "QmlImportScanner"
            self.cpp_info.components["qtQmlImportScanner"].requires = _get_corrected_reqs(["Qml"])
            if qt_quick_enabled:
                _create_module("Quick", ["Gui", "Qml", "QmlModels"])
                if self.options.widgets:
                    _create_module("QuickWidgets", ["Gui", "Qml", "Quick", "Widgets"])
                _create_module("QuickShapes", ["Gui", "Qml", "Quick"])
            _create_module("QmlWorkerScript", ["Qml"])

        if self.options.qttools and self.options.gui and self.options.widgets:
            self.cpp_info.components["qtLinguistTools"].set_property("cmake_target_name", "Qt6::LinguistTools")
            self.cpp_info.components["qtLinguistTools"].names["cmake_find_package"] = "LinguistTools"
            self.cpp_info.components["qtLinguistTools"].names["cmake_find_package_multi"] = "LinguistTools"
            _create_module("UiPlugin", ["Gui", "Widgets"])
            self.cpp_info.components["qtUiPlugin"].libs = [] # this is a collection of abstract classes, so this is header-only
            self.cpp_info.components["qtUiPlugin"].libdirs = []
            _create_module("UiTools", ["UiPlugin", "Gui", "Widgets"])
            _create_module("Designer", ["Gui", "UiPlugin", "Widgets", "Xml"])
            _create_module("Help", ["Gui", "Sql", "Widgets"])

        if self.options.qtquick3d and qt_quick_enabled:
            _create_module("Quick3DUtils", ["Gui"])
            _create_module("Quick3DAssetImport", ["Gui", "Qml", "Quick3DUtils"])
            _create_module("Quick3DRuntimeRender", ["Gui", "Quick", "Quick3DAssetImport", "Quick3DUtils", "ShaderTools"])
            _create_module("Quick3D", ["Gui", "Qml", "Quick", "Quick3DRuntimeRender"])

        if (self.options.get_safe("qtquickcontrols2") or \
            (self.options.qtdeclarative and tools.Version(self.version) >= "6.2.0")) and qt_quick_enabled:
            _create_module("QuickControls2", ["Gui", "Quick"])
            _create_module("QuickTemplates2", ["Gui", "Quick"])

        if self.options.qtshadertools and self.options.gui:
            _create_module("ShaderTools", ["Gui"])

        if self.options.qtsvg and self.options.gui:
            _create_module("Svg", ["Gui"])
            if self.options.widgets:
                _create_module("SvgWidgets", ["Gui", "Svg", "Widgets"])

        if self.options.qtwayland and self.options.gui:
            _create_module("WaylandClient", ["Gui", "wayland::wayland-client"])
            _create_module("WaylandCompositor", ["Gui", "wayland::wayland-server"])

        if self.options.get_safe("qtactiveqt") and self.settings.os == "Windows":
            _create_module("AxBase", ["Gui", "Widgets"])
            _create_module("AxServer", ["AxBase"])
            self.cpp_info.components["qtAxServer"].system_libs.append("shell32")
            self.cpp_info.components["qtAxServer"].defines.append("QAXSERVER")
            _create_module("AxContainer", ["AxBase"])
        if self.options.get_safe("qtcharts"):
            _create_module("Charts", ["Gui", "Widgets"])
        if self.options.get_safe("qtdatavis3d") and qt_quick_enabled:
            _create_module("DataVisualization", ["Gui", "OpenGL", "Qml", "Quick"])
        if self.options.get_safe("qtlottie"):
            _create_module("Bodymovin", ["Gui"])
        if self.options.get_safe("qtscxml"):
            _create_module("StateMachine")
            _create_module("StateMachineQml", ["StateMachine", "Qml"])
            _create_module("Scxml")
            _create_plugin("QScxmlEcmaScriptDataModelPlugin", "qscxmlecmascriptdatamodel", "scxmldatamodel", ["Scxml", "Qml"])
            _create_module("ScxmlQml", ["Scxml", "Qml"])
        if self.options.get_safe("qtvirtualkeyboard") and qt_quick_enabled:
            _create_module("VirtualKeyboard", ["Gui", "Qml", "Quick"])
            _create_plugin("QVirtualKeyboardPlugin", "qtvirtualkeyboardplugin", "platforminputcontexts", ["Gui", "Qml", "VirtualKeyboard"])
            _create_plugin("QtVirtualKeyboardHangulPlugin", "qtvirtualkeyboard_hangul", "virtualkeyboard", ["Gui", "Qml", "VirtualKeyboard"])
            _create_plugin("QtVirtualKeyboardMyScriptPlugin", "qtvirtualkeyboard_myscript", "virtualkeyboard", ["Gui", "Qml", "VirtualKeyboard"])
            _create_plugin("QtVirtualKeyboardThaiPlugin", "qtvirtualkeyboard_thai", "virtualkeyboard", ["Gui", "Qml", "VirtualKeyboard"])
        if self.options.get_safe("qt3d"):
            _create_module("3DCore", ["Gui", "Network"])
            _create_module("3DRender", ["3DCore", "OpenGL"])
            _create_module("3DAnimation", ["3DCore", "3DRender", "Gui"])
            _create_module("3DInput", ["3DCore", "Gui"])
            _create_module("3DLogic", ["3DCore", "Gui"])
            _create_module("3DExtras", ["Gui", "3DCore", "3DInput", "3DLogic", "3DRender"])
            _create_plugin("DefaultGeometryLoaderPlugin", "defaultgeometryloader", "geometryloaders", ["3DCore", "3DRender", "Gui"])
            _create_plugin("fbxGeometryLoaderPlugin", "fbxgeometryloader", "geometryloaders", ["3DCore", "3DRender", "Gui"])
            if qt_quick_enabled:
                _create_module("3DQuick", ["3DCore", "Gui", "Qml", "Quick"])
                _create_module("3DQuickAnimation", ["3DAnimation", "3DCore", "3DQuick", "3DRender", "Gui", "Qml"])
                _create_module("3DQuickExtras", ["3DCore", "3DExtras", "3DInput", "3DQuick", "3DRender", "Gui", "Qml"])
                _create_module("3DQuickInput", ["3DCore", "3DInput", "3DQuick", "Gui", "Qml"])
                _create_module("3DQuickRender", ["3DCore", "3DQuick", "3DRender", "Gui", "Qml"])
                _create_module("3DQuickScene2D", ["3DCore", "3DQuick", "3DRender", "Gui", "Qml"])
        if self.options.get_safe("qtimageformats"):
            _create_plugin("ICNSPlugin", "qicns", "imageformats", ["Gui"])
            _create_plugin("QJp2Plugin", "qjp2", "imageformats", ["Gui"])
            _create_plugin("QMacHeifPlugin", "qmacheif", "imageformats", ["Gui"])
            _create_plugin("QMacJp2Plugin", "qmacjp2", "imageformats", ["Gui"])
            _create_plugin("QMngPlugin", "qmng", "imageformats", ["Gui"])
            _create_plugin("QTgaPlugin", "qtga", "imageformats", ["Gui"])
            _create_plugin("QTiffPlugin", "qtiff", "imageformats", ["Gui"])
            _create_plugin("QWbmpPlugin", "qwbmp", "imageformats", ["Gui"])
            _create_plugin("QWebpPlugin", "qwebp", "imageformats", ["Gui"])
        if self.options.get_safe("qtnetworkauth"):
            _create_module("NetworkAuth", ["Network"])
        if self.options.get_safe("qtcoap"):
            _create_module("Coap", ["Network"])
        if self.options.get_safe("qtmqtt"):
            _create_module("Mqtt", ["Network"])
        if self.options.get_safe("qtopcua"):
            _create_module("OpcUa", ["Network"])
            _create_plugin("QOpen62541Plugin", "open62541_backend", "opcua", ["Network", "OpcUa"])
            _create_plugin("QUACppPlugin", "uacpp_backend", "opcua", ["Network", "OpcUa"])

        if self.options.get_safe("qtmultimedia"):
            multimedia_reqs = ["Network", "Gui"]
            if self.options.get_safe("with_libalsa", False):
                multimedia_reqs.append("libalsa::libalsa")
            if self.options.with_openal:
                multimedia_reqs.append("openal::openal")
            if self.options.get_safe("with_pulseaudio", False):
                multimedia_reqs.append("pulseaudio::pulse")
            _create_module("Multimedia", multimedia_reqs)
            _create_module("MultimediaWidgets", ["Multimedia", "Widgets", "Gui"])
            if self.options.qtdeclarative and qt_quick_enabled:
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

        if (self.options.get_safe("qtlocation") and tools.Version(self.version) < "6.2.2") or \
            (self.options.get_safe("qtpositioning") and tools.Version(self.version) >= "6.2.2"):
            _create_module("Positioning")
            _create_plugin("QGeoPositionInfoSourceFactoryGeoclue2", "qtposition_geoclue2", "position", [])
            _create_plugin("QGeoPositionInfoSourceFactoryPoll", "qtposition_positionpoll", "position", [])

        if self.options.get_safe("qtsensors"):
            _create_module("Sensors")
            _create_plugin("genericSensorPlugin", "qtsensors_generic", "sensors", [])
            _create_plugin("IIOSensorProxySensorPlugin", "qtsensors_iio-sensor-proxy", "sensors", [])
            if self.settings.os == "Linux":
                _create_plugin("LinuxSensorPlugin", "qtsensors_linuxsys", "sensors", [])
            _create_plugin("QtSensorGesturePlugin", "qtsensorgestures_plugin", "sensorgestures", [])
            _create_plugin("QShakeSensorGesturePlugin", "qtsensorgestures_shakeplugin", "sensorgestures", [])

        if self.options.get_safe("qtconnectivity"):
            _create_module("Bluetooth", ["Network"])
            _create_module("Nfc", [])

        if self.options.get_safe("qtserialport"):
            _create_module("SerialPort")

        if self.options.get_safe("qtserialbus"):
            _create_module("SerialBus", ["SerialPort"])
            _create_plugin("PassThruCanBusPlugin", "qtpassthrucanbus", "canbus", [])
            _create_plugin("PeakCanBusPlugin", "qtpeakcanbus", "canbus", [])
            _create_plugin("SocketCanBusPlugin", "qtsocketcanbus", "canbus", [])
            _create_plugin("TinyCanBusPlugin", "qttinycanbus", "canbus", [])
            _create_plugin("VirtualCanBusPlugin", "qtvirtualcanbus", "canbus", [])

        if self.options.get_safe("qtwebsockets"):
            _create_module("WebSockets", ["Network"])

        if self.options.get_safe("qtwebchannel"):
            _create_module("WebChannel", ["Qml"])

        if self.options.get_safe("qtwebengine") and qt_quick_enabled:
            webenginereqs = ["Gui", "Quick", "WebChannel", "Positioning"]
            if self.settings.os == "Linux":
                webenginereqs.extend(["expat::expat", "opus::libopus", "xorg-proto::xorg-proto", "libxshmfence::libxshmfence", \
                                      "nss::nss", "libdrm::libdrm"])
            _create_module("WebEngineCore", webenginereqs)
            _create_module("WebEngineQuick", ["WebEngineCore"])
            _create_module("WebEngineWidgets", ["WebEngineCore", "Quick", "PrintSupport", "Widgets", "Gui", "Network"])

        if self.options.get_safe("qtremoteobjects"):
            _create_module("RemoteObjects")

        if self.options.get_safe("qtwebview"):
            _create_module("WebView", ["Core", "Gui"])

        if self.settings.os in ["Windows", "iOS"]:
            if self.settings.os == "Windows":
                self.cpp_info.components["qtEntryPointImplementation"].set_property("cmake_target_name", "Qt6::EntryPointImplementation")
                self.cpp_info.components["qtEntryPointImplementation"].names["cmake_find_package"] = "EntryPointImplementation"
                self.cpp_info.components["qtEntryPointImplementation"].names["cmake_find_package_multi"] = "EntryPointImplementation"
                self.cpp_info.components["qtEntryPointImplementation"].libs = ["Qt6EntryPoint%s" % libsuffix]
                self.cpp_info.components["qtEntryPointImplementation"].system_libs = ["shell32"]

                if self.settings.compiler == "gcc":
                    self.cpp_info.components["qtEntryPointMinGW32"].set_property("cmake_target_name", "Qt6::EntryPointMinGW32")
                    self.cpp_info.components["qtEntryPointMinGW32"].names["cmake_find_package"] = "EntryPointMinGW32"
                    self.cpp_info.components["qtEntryPointMinGW32"].names["cmake_find_package_multi"] = "EntryPointMinGW32"
                    self.cpp_info.components["qtEntryPointMinGW32"].system_libs = ["mingw32"]
                    self.cpp_info.components["qtEntryPointMinGW32"].requires = ["qtEntryPointImplementation"]

            self.cpp_info.components["qtEntryPointPrivate"].set_property("cmake_target_name", "Qt6::EntryPointPrivate")
            self.cpp_info.components["qtEntryPointPrivate"].names["cmake_find_package"] = "EntryPointPrivate"
            self.cpp_info.components["qtEntryPointPrivate"].names["cmake_find_package_multi"] = "EntryPointPrivate"
            if self.settings.os == "Windows":
                if self.settings.compiler == "gcc":
                    self.cpp_info.components["qtEntryPointPrivate"].defines.append("QT_NEEDS_QMAIN")
                    self.cpp_info.components["qtEntryPointPrivate"].requires.append("qtEntryPointMinGW32")
                else:
                    self.cpp_info.components["qtEntryPointPrivate"].requires.append("qtEntryPointImplementation")
            if self.settings.os == "iOS":
                self.cpp_info.components["qtEntryPointPrivate"].exelinkflags.append("-Wl,-e,_qt_main_wrapper")

        if self.settings.os != "Windows":
            self.cpp_info.components["qtCore"].cxxflags.append("-fPIC")

        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.components["qtCore"].system_libs.append("version")  # qtcore requires "GetFileVersionInfoW" and "VerQueryValueW" which are in "Version.lib" library
                self.cpp_info.components["qtCore"].system_libs.append("winmm")    # qtcore requires "__imp_timeSetEvent" which is in "Winmm.lib" library
                self.cpp_info.components["qtCore"].system_libs.append("netapi32") # qtcore requires "NetApiBufferFree" which is in "Netapi32.lib" library
                self.cpp_info.components["qtCore"].system_libs.append("userenv")  # qtcore requires "__imp_GetUserProfileDirectoryW " which is in "UserEnv.Lib" library
                self.cpp_info.components["qtCore"].system_libs.append("ws2_32")  # qtcore requires "WSAStartup " which is in "Ws2_32.Lib" library
                self.cpp_info.components["qtNetwork"].system_libs.append("dnsapi")  # qtnetwork from qtbase requires "DnsFree" which is in "Dnsapi.lib" library
                self.cpp_info.components["qtNetwork"].system_libs.append("iphlpapi")
                self.cpp_info.components["qtNetwork"].system_libs.extend(["winhttp", "secur32"])


            if self.settings.os == "Macos":
                self.cpp_info.components["qtCore"].frameworks.append("IOKit")     # qtcore requires "_IORegistryEntryCreateCFProperty", "_IOServiceGetMatchingService" and much more which are in "IOKit" framework
                self.cpp_info.components["qtCore"].frameworks.append("Cocoa")     # qtcore requires "_OBJC_CLASS_$_NSApplication" and more, which are in "Cocoa" framework
                self.cpp_info.components["qtCore"].frameworks.append("Security")  # qtcore requires "_SecRequirementCreateWithString" and more, which are in "Security" framework
                self.cpp_info.components["qtNetwork"].frameworks.append("SystemConfiguration")
                if self.options.with_gssapi:
                    self.cpp_info.components["qtNetwork"].frameworks.append("GSS")
                if self.options.gui and self.options.widgets:
                    self.cpp_info.components["qtPrintSupport"].system_libs.append("cups")

        self.cpp_info.components["qtCore"].builddirs.append(os.path.join("res","archdatadir","bin"))
        build_modules.append(self._cmake_executables_file)
        self.cpp_info.components["qtCore"].build_modules["cmake_find_package"].append(self._cmake_executables_file)
        self.cpp_info.components["qtCore"].build_modules["cmake_find_package_multi"].append(self._cmake_executables_file)
        build_modules.append(self._cmake_qt6_private_file("Core"))
        self.cpp_info.components["qtCore"].build_modules["cmake_find_package"].append(self._cmake_qt6_private_file("Core"))
        self.cpp_info.components["qtCore"].build_modules["cmake_find_package_multi"].append(self._cmake_qt6_private_file("Core"))
        if self.settings.os in ["Windows", "iOS"]:
            build_modules.append(self._cmake_entry_point_file)
            self.cpp_info.components["qtCore"].build_modules["cmake_find_package"].append(self._cmake_entry_point_file)
            self.cpp_info.components["qtCore"].build_modules["cmake_find_package_multi"].append(self._cmake_entry_point_file)

        for m in os.listdir(os.path.join("lib", "cmake")):
            module = os.path.join("lib", "cmake", m, "%sMacros.cmake" % m)
            component_name = m.replace("Qt6", "qt")
            if component_name == "qt":
                component_name = "qtCore"
            if os.path.isfile(module):
                build_modules.append(module)
                self.cpp_info.components[component_name].build_modules["cmake_find_package"].append(module)
                self.cpp_info.components[component_name].build_modules["cmake_find_package_multi"].append(module)

            helper_modules = glob.glob(os.path.join(self.package_folder, "lib", "cmake", m, "QtPublic*Helpers.cmake"))
            build_modules.extend(helper_modules)
            self.cpp_info.components[component_name].build_modules["cmake_find_package"].extend(helper_modules)
            self.cpp_info.components[component_name].build_modules["cmake_find_package_multi"].extend(helper_modules)
            self.cpp_info.components[component_name].builddirs.append(os.path.join("lib", "cmake", m))

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
