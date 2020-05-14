from conans import ConanFile, CMake, tools
import os
import platform


class QtWebKitConan(ConanFile):
    name = "qtwebkit"
    version = "5.212.0-alpha4"
    license = "LGPL-2.0-or-later, LGPL-2.1-or-later, BSD-2-Clause"
    homepage = "https://github.com/qtwebkit/qtwebkit"
    description = "Qt port of WebKit"
    topics = ("qt", "browser-engine", "webkit", "qt5", "qml", "qtwebkit")
    settings = "os", "compiler", "build_type", "arch"
    generators = 'cmake'
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

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

    requires = (
        "qt/5.14.1",
        "libjpeg-turbo/2.0.4",
        "libpng/1.6.37",
        "libwebp/1.1.0",
        "sqlite3/3.31.0",
        "icu/64.2",
        "libxml2/2.9.9",
        "libxslt/1.1.33",
        "zlib/1.2.11"
    )

    def build_requirements(self):
        pass

    def requirements(self):
        if self.options["with_webcrypto"]:
            self.requires("libgcrypt/1.8.4@bincrafters/stable")

        if self.options["with_gstreamer"]:
            self.requires["gstreamer/1.16.0@bincrafters/stable"]

        if self.options["with_libhyphen"]:
            pass # TODO add dependency when somebody will write receipt for libhyphen

        if self.options["with_woff2"]:
            pass # TODO wait until https://github.com/qtwebkit/conan-woff2 will be deployed on bintray

    def source(self):
        tools.get(f'{self.homepage}/releases/download/{self.name}-{self.version}/{self.name}-{self.version}.tar.xz',
                  sha256='9ca126da9273664dd23a3ccd0c9bebceb7bb534bddd743db31caf6a5a6d4a9e6')
        os.rename(f'{self.name}-{self.version}', self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["PORT"] = "Qt"
        cmake.definitions["ENABLE_DEVICE_ORIENTATION"] = "OFF"
        cmake.definitions["ENABLE_TEST_SUPPORT"] = "OFF"

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
        cmake = self._configure_cmake()
        cmake.build()
        cmake.install()

    def package(self):
        pass

    def package_info(self):
        libs = ("QtWebKit", "QtWebKitWidgets")

        if tools.is_apple_os(self.settings.os):           
            self.cpp_info.frameworkdirs = ['lib']
            self.cpp_info.frameworks = [lib for lib in libs]
        else:
            self.cpp_info.libdirs.append('lib')
            self.cpp_info.libs = [lib for lib in libs]

        self.env_info.CMAKE_PREFIX_PATH.append(self.package_folder)
