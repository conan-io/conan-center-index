import os
import shutil
import glob

import configparser
from conans import ConanFile, tools, RunEnvironment, CMake
from conans.errors import ConanInvalidConfiguration
from conans.model import Generator


class qt(Generator):
    @property
    def filename(self):
        return "qt.conf"

    @property
    def content(self):
        return "[Paths]\nPrefix = %s\n" % self.conanfile.deps_cpp_info["qt"].rootpath.replace("\\", "/")


class QtConan(ConanFile):
    _submodules = ["qtsvg", "qtdeclarative", "qttools", "qttranslations", "qtdoc",
    "qtwayland","qtquickcontrols2", "qtquicktimeline", "qtquick3d", "qtshadertools", "qt5compat"]

    generators = "pkg_config", "cmake_find_package", "cmake"
    name = "qt"
    description = "Qt is a cross-platform framework for graphical user interfaces."
    topics = ("conan", "qt", "ui")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.qt.io"
    license = "LGPL-3.0"
    exports = ["patches/*.diff"]
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

        "gui": [True, False],
        "widgets": [True, False],

        "device": "ANY",
        "cross_compile": "ANY",
        "sysroot": "ANY",
        "multiconfiguration": [True, False],
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
        "with_harfbuzz": False,
        "with_libjpeg": False,
        "with_libpng": True,
        "with_sqlite3": True,
        "with_mysql": False,
        "with_pq": True,
        "with_odbc": True,
        "with_zstd": False,

        "gui": True,
        "widgets": True,

        "device": None,
        "cross_compile": None,
        "sysroot": None,
        "multiconfiguration": False,
    }
    default_options.update({module: False for module in _submodules})

    short_paths = True

    _cmake = None

    def export(self):
        self.copy("qtmodules%s.conf" % self.version)

    def build_requirements(self):
        self.build_requires("cmake/3.19.1")
        self.build_requires("ninja/1.10.2")
        self.build_requires('pkgconf/1.7.3')
        if self.settings.compiler == "Visual Studio":
            self.build_requires('strawberryperl/5.30.0.1')

    def config_options(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_icu
            del self.options.with_fontconfig
            self.options.with_glib = False
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "8":
            raise ConanInvalidConfiguration("qt 6 does not support GCC before 8")
        if self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) < "9":
            raise ConanInvalidConfiguration("qt 6 does not support clang before 9")
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < "16":
            raise ConanInvalidConfiguration("qt 6 does not support Visual Studio before 2019")
        if self.settings.compiler == "apple-clang" and tools.Version(self.settings.compiler.version) < "11":
            raise ConanInvalidConfiguration("qt 6 does not support apple-clang before 11")
        if self.settings.os == "Windows":
            self.options.opengl = "dynamic"

    def configure(self):

        if self.options.widgets and not self.options.gui:
            raise ConanInvalidConfiguration("using option qt:widgets without option qt:gui is not possible. "
                                            "You can either disable qt:widgets or enable qt:gui")
        if not self.options.gui:
            del self.options.opengl
            del self.options.with_vulkan
            del self.options.with_freetype
            del self.options.with_fontconfig
            del self.options.with_harfbuzz
            del self.options.with_libjpeg
            del self.options.with_libpng

        if self.settings.os == "Android" and self.options.get_safe("opengl", "no") == "desktop":
            raise ConanInvalidConfiguration("OpenGL desktop is not supported on Android.")

        if self.settings.os != "Windows" and self.options.get_safe("opengl", "no") == "dynamic":
            raise ConanInvalidConfiguration("Dynamic OpenGL is supported only on Windows.")

        if self.options.get_safe("with_fontconfig", False) and not self.options.get_safe("with_freetype", False):
            raise ConanInvalidConfiguration("with_fontconfig cannot be enabled if with_freetype is disabled.")

        if self.options.multiconfiguration:
            del self.settings.build_type

        if "MT" in self.settings.get_safe("compiler.runtime", default="") and self.options.shared:
            raise ConanInvalidConfiguration("Qt cannot be built as shared library with static runtime")

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
            assert(m in ["qtbase", "qtqa", "qtrepotools"] or m in self._submodules)

        for m in self._submodules:
            assert(m in submodules_tree)

        def _enablemodule(mod):
            if mod != "qtbase":
                setattr(self.options, mod, True)
            for req in submodules_tree[mod]["depends"]:
                _enablemodule(req)

        for module in self._submodules:
            if self.options.get_safe(module):
                _enablemodule(module)

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.openssl:
            self.requires("openssl/1.1.1i")
        if self.options.with_pcre2:
            self.requires("pcre2/10.35")
        if self.options.with_vulkan:
            self.requires("vulkan-loader/1.2.162.0")

        if self.options.with_glib:
            self.requires("glib/2.67.1")
        if self.options.with_doubleconversion and not self.options.multiconfiguration:
            self.requires("double-conversion/3.1.5")
        if self.options.get_safe("with_freetype", False) and not self.options.multiconfiguration:
            self.requires("freetype/2.10.4")
        if self.options.get_safe("with_fontconfig", False):
            self.requires("fontconfig/2.13.92")
        if self.options.get_safe("with_icu", False):
            self.requires("icu/68.2")
        if self.options.get_safe("with_harfbuzz", False) and not self.options.multiconfiguration:
            self.requires("harfbuzz/2.7.4")
        if self.options.get_safe("with_libjpeg", False) and not self.options.multiconfiguration:
            if self.options.with_libjpeg == "libjpeg-turbo":
                self.requires("libjpeg-turbo/2.0.6")
            else:
                self.requires("libjpeg/9d")
        if self.options.get_safe("with_libpng", False) and not self.options.multiconfiguration:
            self.requires("libpng/1.6.37")
        if self.options.with_sqlite3 and not self.options.multiconfiguration:
            self.requires("sqlite3/3.33.0")
            self.options["sqlite3"].enable_column_metadata = True
        if self.options.get_safe("with_mysql", False):
            self.requires("libmysqlclient/8.0.17")
        if self.options.with_pq:
            self.requires("libpq/12.2")
        if self.options.with_odbc:
            if self.settings.os != "Windows":
                self.requires("odbc/2.3.7")
        if self.options.gui and self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system")
            if not tools.cross_building(self, skip_x64_x86=True):
                self.requires("xkbcommon/1.0.3")
        if self.settings.os != "Windows" and self.options.get_safe("opengl", "no") != "no":
            self.requires("opengl/system")
        if self.options.with_zstd:
            self.requires("zstd/1.4.8")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        shutil.move("qt-everywhere-src-%s" % self.version, "qt6")

        # patching in source method because of no_copy_source attribute

        tools.replace_in_file(os.path.join("qt6", "CMakeLists.txt"),
                        "enable_testing()",
                        "include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)\nconan_basic_setup(KEEP_RPATHS)\n"
                               "set(QT_EXTRA_INCLUDEPATHS ${CONAN_INCLUDE_DIRS})\n"
                               "set(QT_EXTRA_DEFINES ${CONAN_DEFINES})\n"
                               "set(QT_EXTRA_LIBDIRS ${CONAN_LIB_DIRS})\n"
                               "enable_testing()")

        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        tools.replace_in_file(os.path.join("qt6", "qtbase", "cmake", "QtInternalTargets.cmake"),
                              "target_compile_options(PlatformCommonInternal INTERFACE -Zc:wchar_t)",
                              "target_compile_options(PlatformCommonInternal INTERFACE -Zc:wchar_t -Zc:twoPhase-)")

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

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self, generator="Ninja")

        self._cmake.definitions["INSTALL_MKSPECSDIR"] = os.path.join(self.package_folder, "res", "archdatadir", "mkspecs")
        self._cmake.definitions["INSTALL_ARCHDATADIR"] = os.path.join(self.package_folder, "res", "archdatadir")
        self._cmake.definitions["INSTALL_DATADIR"] = os.path.join(self.package_folder, "res", "datadir")
        self._cmake.definitions["INSTALL_SYSCONFDIR"] = os.path.join(self.package_folder, "res", "sysconfdir")

        self._cmake.definitions["QT_BUILD_TESTS"] = "OFF"
        self._cmake.definitions["QT_BUILD_EXAMPLES"] = "OFF"

        if self.settings.compiler == "Visual Studio":
            if self.settings.compiler.runtime == "MT" or self.settings.compiler.runtime == "MTd":
                self._cmake.definitions["FEATURE_static_runtime"] = "ON"

        if self.options.multiconfiguration:
            self._cmake.generator = "Ninja Multi-Config"
            self._cmake.definitions["CMAKE_CONFIGURATION_TYPES"] = "Release;Debug"
        self._cmake.definitions["FEATURE_optimize_size"] = ("ON" if self.settings.build_type == "MinSizeRel" else "OFF")

        for module in self._submodules:
            if module != 'qtbase':
                self._cmake.definitions["BUILD_%s" % module] = ("ON" if self.options.get_safe(module) else "OFF")

        self._cmake.definitions["FEATURE_system_zlib"] = "ON"

        self._cmake.definitions["INPUT_opengl"] = self.options.opengl

        # openSSL
        if not self.options.openssl:
            self._cmake.definitions["INPUT_openssl"] = "no"
        else:
            if self.options["openssl"].shared:
                self._cmake.definitions["INPUT_openssl"] = "runtime"
            else:
                self._cmake.definitions["INPUT_openssl"] = "linked"


        for opt, conf_arg in [("with_glib", "glib"),
                              ("with_icu", "icu"),
                              ("with_fontconfig", "fontconfig"),
                              ("with_mysql", "sql_mysql"),
                              ("with_pq", "sql_psql"),
                              ("with_odbc", "sql_odbc"),
                              ("gui", "gui"),
                              ("widgets", "widgets"),
                              ("with_zstd", "zstd"),
                              ("with_vulkan", "vulkan")]:
            self._cmake.definitions["FEATURE_%s" % conf_arg] = ("ON" if self.options.get_safe(opt, False) else "OFF")


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
                    self._cmake.definitions["FEATURE_%s" % conf_arg] = "ON"
                else:
                    self._cmake.definitions["FEATURE_system_%s" % conf_arg] = "ON"
            else:
                self._cmake.definitions["FEATURE_%s" % conf_arg] = "OFF"
                self._cmake.definitions["FEATURE_system_%s" % conf_arg] = "OFF"

        if self.settings.os == "Macos":
            self._cmake.definitions["FEATURE_framework"] = "OFF"
        elif self.settings.os == "Android":
            self._cmake.definitions["CMAKE_ANDROID_NATIVE_API_LEVEL"] = self.settings.os.api_level
            self._cmake.definitions["ANDROID_ABI"] =  {"armv7": "armeabi-v7a",
                                           "armv8": "arm64-v8a",
                                           "x86": "x86",
                                           "x86_64": "x86_64"}.get(str(self.settings.arch))

        if self.options.sysroot:
            self._cmake.definitions["CMAKE_SYSROOT"] = self.options.sysroot

        if self.options.device:
            self._cmake.definitions["QT_QMAKE_TARGET_MKSPEC"] = os.path.join("devices", self.options.device)
        else:
            xplatform_val = self._xplatform()
            if xplatform_val:
                self._cmake.definitions["QT_QMAKE_TARGET_MKSPEC"] = xplatform_val
            else:
                self.output.warn("host not supported: %s %s %s %s" %
                                 (self.settings.os, self.settings.compiler,
                                  self.settings.compiler.version, self.settings.arch))
        if self.options.cross_compile:
            self._cmake.definitions["QT_QMAKE_DEVICE_OPTIONS"] = "CROSS_COMPILE=%s" % self.options.cross_compile

        self._cmake.definitions["FEATURE_pkg_config"] = "ON"
        if self.settings.compiler == "gcc" and self.settings.build_type == "Debug" and not self.options.shared:
            self._cmake.definitions["BUILD_WITH_PCH"]= "OFF" # disabling PCH to save disk space

        try:
            self._cmake.configure(source_folder="qt6")
        except:
            self.output.info(tools.load(os.path.join(self.build_folder, "CMakeFiles", "CMakeError.log")))
            self.output.info(tools.load(os.path.join(self.build_folder, "CMakeFiles", "CMakeOutput.log")))
            raise
        return self._cmake

    def build(self):
        for f in glob.glob("*.cmake"):
            tools.replace_in_file(f,
                "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:>",
                "", strict=False)
            tools.replace_in_file(f,
                "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:>",
                "", strict=False)
            tools.replace_in_file(f,
                "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:>",
                "", strict=False)
            tools.replace_in_file(f,
                "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:-Wl,--export-dynamic>",
                "", strict=False)
            tools.replace_in_file(f,
                "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:-Wl,--export-dynamic>",
                "", strict=False)
        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            # next lines force cmake package to be in PATH before the one provided by visual studio (vcvars)
            build_env = tools.RunEnvironment(self).vars if self.settings.compiler == "Visual Studio" else {}
            build_env["MAKEFLAGS"] = "j%d" % tools.cpu_count()
            build_env["PKG_CONFIG_PATH"] = [self.build_folder]
            if self.settings.os == "Windows":
                build_env["PATH"].append(os.path.join(self.source_folder, "qt6", "gnuwin32", "bin"))
            if self.settings.compiler == "Visual Studio":
                # this avoids cmake using gcc from strawberryperl
                build_env["CC"] = "cl"
                build_env["CXX"] = "cl"
            with tools.environment_append(build_env):

                if tools.os_info.is_macos:
                    open(".qmake.stash" , "w").close()
                    open(".qmake.super" , "w").close()

                cmake = self._configure_cmake()
                if tools.os_info.is_macos:
                    with open("bash_env", "w") as f:
                        f.write('export DYLD_LIBRARY_PATH="%s"' % ":".join(RunEnvironment(self).vars["DYLD_LIBRARY_PATH"]))
                with tools.environment_append({
                    "BASH_ENV": os.path.abspath("bash_env")
                }) if tools.os_info.is_macos else tools.no_op():
                    with tools.run_environment(self):
                        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        with open(os.path.join(self.package_folder, "bin", "qt.conf"), "w") as f:
            f.write("""[Paths]
Prefix = ..
ArchData = res/archdatadir
HostData = res/archdatadir
Data = res/datadir
Sysconf = res/sysconfdir
LibraryExecutables = res/archdatadir/bin
Plugins = res/archdatadir/plugins
Imports = res/archdatadir/imports
Qml2Imports = res/archdatadir/qml
Translations = res/datadir/translations
Documentation = res/datadir/doc
Examples = res/datadir/examples""")
        self.copy("*LICENSE*", src="qt6/", dst="licenses")
        for module in self._submodules:
            if not self.options.get_safe(module):
                tools.rmdir(os.path.join(self.package_folder, "licenses", module))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la*")
        tools.remove_files_by_mask(self.package_folder, "*.pdb*")
        os.remove(os.path.join(self.package_folder, "bin", "qt-cmake-private-install.cmake"))

    def package_id(self):
        del self.info.options.cross_compile
        del self.info.options.sysroot
        if self.options.multiconfiguration and self.settings.compiler == "Visual Studio":
            if "MD" in self.settings.compiler.runtime:
                self.info.settings.compiler.runtime = "MD/MDd"
            else:
                self.info.settings.compiler.runtime = "MT/MTd"

    def package_info(self):
        # FIXME add components
        self.cpp_info.libs = tools.collect_libs(self)

        # Add top level include directory, so code compile if someone uses
        # includes with prefixes (e.g. "#include <QtCore/QString>")
        self.cpp_info.includedirs = ["include"]

        # Add all Qt module directories (QtCore, QtGui, QtWidgets and so on), so prefix
        # can be omited in includes (e.g. "#include <QtCore/QString>" => "#include <QString>")
        fu = ["include/" + f.name for f in os.scandir("include") if f.is_dir()]
        self.cpp_info.includedirs.extend(fu)

        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs.append("Version")  # qtcore requires "GetFileVersionInfoW" and "VerQueryValueW" which are in "Version.lib" library
                self.cpp_info.system_libs.append("Winmm")    # qtcore requires "__imp_timeSetEvent" which is in "Winmm.lib" library
                self.cpp_info.system_libs.append("Netapi32") # qtcore requires "NetApiBufferFree" which is in "Netapi32.lib" library
                self.cpp_info.system_libs.append("UserEnv")  # qtcore requires "__imp_GetUserProfileDirectoryW " which is in "UserEnv.Lib" library

            if self.settings.os == "Macos":
                self.cpp_info.frameworks.append("IOKit")     # qtcore requires "_IORegistryEntryCreateCFProperty", "_IOServiceGetMatchingService" and much more which are in "IOKit" framework
                self.cpp_info.frameworks.append("Cocoa")     # qtcore requires "_OBJC_CLASS_$_NSApplication" and more, which are in "Cocoa" framework
                self.cpp_info.frameworks.append("Security")  # qtcore requires "_SecRequirementCreateWithString" and more, which are in "Security" framework
