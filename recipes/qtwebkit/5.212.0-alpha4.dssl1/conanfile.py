from conans import ConanFile, CMake, tools
import os
import platform


class QtWebKitConan(ConanFile):
    name = "qtwebkit"
    version = "5.212.0-alpha4.dssl1"
    original_version = "5.212.0-alpha4"
    license = "LGPL-2.0-or-later, LGPL-2.1-or-later, BSD-2-Clause"
    homepage = "https://github.com/qtwebkit/qtwebkit"
    description = "Qt port of WebKit"
    topics = ("qt", "browser-engine", "webkit", "qt5", "qml", "qtwebkit")
    settings = "os", "compiler", "build_type", "arch"
    generators = 'cmake'
    exports_sources = [
        "patches/*.patch"
    ]
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    short_paths = True

    options = {
        "with_bmalloc": [True, False],
        "with_geolocation": [True, False],
        "with_gstreamer": [True, False],
        "with_libhyphen": [True, False],
        "with_webcrypto": [True, False],
        "with_webkit2": [True, False],
        "with_woff2": [True, False]
        }

    default_options = {
        "with_bmalloc": False,
        "with_geolocation": False,
        "with_gstreamer": False,
        "with_libhyphen": False,
        "with_webcrypto": False,
        "with_webkit2": False,
        "with_woff2": False
    }

    requires = [
        "qt/5.14.1.dssl1",
        "libjpeg-turbo/2.0.4",
        "libpng/1.6.37",
        "libwebp/1.1.0",
        "sqlite3/3.31.0",
        "icu/64.2",
        "libxml2/2.9.9",
        "libxslt/1.1.33",
        "zlib/1.2.11"
    ]

    if platform.system() == "Linux":
        requires.append("libxcomposite/0.4.5")

    def build_requirements(self):
        if tools.os_info.is_windows:
            if not tools.which("bison") or not tools.which("flex"):
                self.build_requires("winflexbison/2.5.22")
        else:
            if not tools.which("bison"):
                self.build_requires("bison/3.5.3")
            if not tools.which("flex"):
                self.build_requires("flex/2.6.4")

        if not tools.which("gperf"):
            self.build_requires("gperf/3.1")
        if not tools.which("ruby"):
            self.build_requires("ruby/2.3.7")

    def requirements(self):
        if self.options["with_webcrypto"]:
            self.requires("libgcrypt/1.8.4@bincrafters/stable")

        if self.options["with_gstreamer"]:
            self.requires("gstreamer/1.16.0@bincrafters/stable")

        if self.options["with_libhyphen"]:
            pass # TODO add dependency when somebody will write receipt for libhyphen

        if self.options["with_woff2"]:
            pass # TODO wait until https://github.com/qtwebkit/conan-woff2 will be deployed on bintray

    def source(self):
        tools.get(f'{self.homepage}/releases/download/{self.name}-{self.original_version}/{self.name}-{self.original_version}.tar.xz',
                  sha256='9ca126da9273664dd23a3ccd0c9bebceb7bb534bddd743db31caf6a5a6d4a9e6')
        os.rename(f'{self.name}-{self.original_version}', self._source_subfolder)

        # check recipe conistency
        tools.check_with_algorithm_sum("sha1", "patches/clang-11-jsc.patch", "03358658f12a895d00f5a7544618dc7019fb2882")
        tools.check_with_algorithm_sum("sha1", "patches/OptionsQt.patch", "d8587c6ce3d498f71888f90890780df8387b0f48")
        tools.check_with_algorithm_sum("sha1", "patches/cmake_version.patch", "030c7f2d1d6daceee54497eac6c734af457f10bf")
        # apply patches
        tools.patch(base_path=self._source_subfolder, patch_file="patches/clang-11-jsc.patch", strip=1)

        if platform.system() == "Linux":
            tools.patch(base_path=self._source_subfolder, patch_file="patches/OptionsQt.patch", strip=1)
            tools.patch(base_path=self._source_subfolder, patch_file="patches/cmake_version.patch", strip=1)

    def _configure_cmake(self):
        cmake = CMake(self, generator="Ninja", build_type=self.settings.build_type)
        
        cmake.definitions["PORT"] = "Qt"
        cmake.definitions["ENABLE_DEVICE_ORIENTATION"] = "OFF"
        cmake.definitions["ENABLE_TEST_SUPPORT"] = "OFF"

        if tools.os_info.is_linux:
            cmake.definitions["USE_OPENGL"] = 1

        # TODO on linux we should check kernel version. On kernels < 3.4 bmalloc cannot be compiled
        if not self.options["with_bmalloc"]:
            cmake.definitions["USE_SYSTEM_MALLOC"] = "ON"
        if not self.options["with_geolocation"]:
            # TODO check if QtLocation module was built
            cmake.definitions["ENABLE_GEOLOCATION"] = "OFF"
        if not self.options["with_gstreamer"]:
            cmake.definitions["USE_GSTREAMER"] = "OFF"
        if not self.options["with_libhyphen"]:
            cmake.definitions["USE_LIBHYPHEN"] = "OFF"
        if not self.options["with_webcrypto"]:
            cmake.definitions["ENABLE_WEB_CRYPTO"] = "OFF"
        if not self.options["with_webkit2"]:
            cmake.definitions["ENABLE_WEBKIT2"] = "OFF"
            cmake.definitions["ENABLE_QT_GESTURE_EVENTS"] = "OFF"
        if not self.options["with_woff2"]:
            cmake.definitions["USE_WOFF2"] = "OFF"

        cmake.definitions["QT_CONAN_DIR"] = os.getcwd()

        qt_dir = self.deps_cpp_info["qt"]
        cmake.definitions["Qt5_DIR"] = os.path.join(qt_dir.libdirs[0], "cmake", "Qt5")

        cmake.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)

        return cmake

    def build(self):
        # Github Actions uses predefined images of OS
        # Mono framework goes pre-installed in macos image, causing path
        # errors in some (png, jpeg, sqlite) CMake finders during header search
        if os.getenv('GITHUB_ACTIONS'):
            if tools.is_apple_os(self.settings.os):
                self.run("sudo rm -rf /Library/Frameworks/Mono.framework")
        with tools.environment_append({"PATH": self.deps_cpp_info.bin_paths}) if tools.os_info.is_windows else tools.no_op():
            cmake = self._configure_cmake()
            cmake.build()
            cmake.install()

    def package(self):
        pass

    def package_info(self):
        if tools.is_apple_os(self.settings.os):
           libs = ["QtWebKit", "QtWebKitWidgets"]
        else:
           libs = ["Qt5WebKit", "Qt5WebKitWidgets"]

        if tools.is_apple_os(self.settings.os):
            self.cpp_info.frameworkdirs = ['lib']
            self.cpp_info.frameworks = libs[:]
        else:
            self.cpp_info.libdirs.append('lib')
            self.cpp_info.libs = libs[:]

        self.env_info.CMAKE_PREFIX_PATH.append(self.package_folder)
