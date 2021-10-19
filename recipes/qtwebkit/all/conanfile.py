from conans import ConanFile, CMake, tools
import os
import platform


class QtWebKitConan(ConanFile):
    name = "qtwebkit"
    original_version = "5.212.0-alpha4"
    license = "LGPL-2.0-or-later, LGPL-2.1-or-later, BSD-2-Clause"
    homepage = "https://github.com/qtwebkit/qtwebkit"
    description = "Qt port of WebKit"
    topics = ("qt", "browser-engine", "webkit", "qt5", "qml", "qtwebkit")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"
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
        "qt/5.14.1.dssl2",
        "libjpeg/9d.dssl2",
        "libpng/1.6.37",
        "libwebp/1.1.0",
        "sqlite3/3.31.0.dssl2",
        "icu/64.2.dssl2",
        "libxml2/2.9.9",
        "libxslt/1.1.33",
        "zlib/1.2.11"
    ]

    def build_requirements(self):
        if tools.os_info.is_windows:
            if not tools.which("bison") or not tools.which("flex"):
                self.build_requires("winflexbison/2.5.22")
        else:
            if not tools.which("bison"):
                self.build_requires("bison/3.5.3")
            if not tools.which("flex"):
                self.build_requires("flex/2.6.4")
        if not tools.which('perl') and tools.os_info.is_windows:
            self.build_requires('strawberryperl/5.30.0.1')
        if not tools.which("gperf"):
            self.build_requires("gperf/3.1.dssl1")
        if not tools.which("ruby"):
            self.build_requires("ruby/2.3.7")

    def requirements(self):
        if platform.system() == "Linux":
            self.requires("libxcomposite/0.4.5")

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
        tools.check_with_algorithm_sum("sha1", "patches/OptionsQt.patch", "b51dbd74b78bbf54ea12145583c980c64bb17074")
        tools.check_with_algorithm_sum("sha1", "patches/cmake_version.patch", "06907610b577145b11c6412decdf0fec8406b45a")
        # apply patches
        tools.patch(base_path=self._source_subfolder, patch_file="patches/clang-11-jsc.patch", strip=1)
        tools.patch(base_path=self._source_subfolder, patch_file="patches/OptionsQt.patch", strip=1)
        if tools.os_info.is_linux:
            tools.patch(base_path=self._source_subfolder, patch_file="patches/cmake_version.patch", strip=1)

        os.remove(os.path.join(self._source_subfolder, 'Source', 'cmake', 'FindICU.cmake'))
        os.remove(os.path.join(self._source_subfolder, 'Source', 'cmake', 'FindSqlite.cmake'))

    def _configure_cmake(self):
        cmake = CMake(self, generator="Ninja", build_type=self.settings.build_type)
        
        cmake.definitions["PORT"] = "Qt"
        cmake.definitions["ENABLE_DEVICE_ORIENTATION"] = "OFF"
        cmake.definitions["ENABLE_TEST_SUPPORT"] = "OFF"

        if tools.os_info.is_linux:
            cmake.definitions["USE_OPENGL"] = 1
            cmake.definitions["ENABLE_OPENGL"] = 1

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

        if hasattr(self.deps_user_info['qt'], '_extra_cmake_variables_'):
            for key, value in self.deps_user_info['qt']._extra_cmake_variables_.items():
                cmake.definitions[key] = value
        if hasattr(self.deps_user_info['qt'], '_extra_cmake_paths_'):
            for key, pathes in self.deps_user_info['qt']._extra_cmake_paths_.items():
                cmake.definitions[key] = ";".join([os.path.join(self.deps_cpp_info['qt'].rootpath, p) for p in pathes])

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
        self.cpp_info.names["cmake_find_package"] = "QtWebKit"
        self.cpp_info.names["cmake_find_package_multi"] = "QtWebKit"

        self.cpp_info.components["WebKit"].names["cmake_find_package"] = "WebKit"
        self.cpp_info.components["WebKit"].names["cmake_find_package_multi"] = "WebKit"
        self.cpp_info.components["WebKit"].includedirs = ["include", os.path.join("include", "QtWebKit")]
        reqs = [
            "qt::qt", 
            "libxml2::libxml2", 
            "libjpeg::libjpeg", 
            "icu::icu",
            "libwebp::libwebp",
            "libpng::libpng",
            "sqlite3::sqlite3",
            "libxslt::libxslt",
            "zlib::zlib"
        ]
        
        if platform.system() == "Linux":
            reqs.append('libxcomposite::libxcomposite')

        if self.options["with_webcrypto"]:
            reqs.append("libgcrypt::libgcrypt")

        if self.options["with_gstreamer"]:
            reqs.append("gstreamer::gstreamer")

        self.cpp_info.components["WebKit"].requires = reqs

        self.cpp_info.components["WebKitWidgets"].names["cmake_find_package"] = "WebKitWidgets"
        self.cpp_info.components["WebKitWidgets"].names["cmake_find_package_multi"] = "WebKitWidgets"
        self.cpp_info.components["WebKitWidgets"].includedirs = ["include", os.path.join("include", "WebKitWidgets")]
        self.cpp_info.components["WebKitWidgets"].requires = [
            "WebKit"
        ]

        if tools.is_apple_os(self.settings.os):
            self.cpp_info.components["WebKit"].frameworks = ["QtWebKit"]
            self.cpp_info.components["WebKitWidgets"].frameworks = ["QtWebKitWidgets"]
        else:
            self.cpp_info.components["WebKit"].libs = ["Qt5WebKit"]
            self.cpp_info.components["WebKitWidgets"].libs = ["Qt5WebKitWidgets"]

        self.env_info.CMAKE_PREFIX_PATH.append(self.package_folder)
