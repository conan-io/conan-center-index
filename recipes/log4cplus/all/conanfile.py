import os
from conan.tools import files
from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.35.0"


class Log4cplusConan(ConanFile):
    name = "log4cplus"
    description = "simple to use C++ logging API, modelled after the Java log4j API"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/log4cplus/log4cplus"
    topics = ("log4cplus", "logging", "log", "logging-library")
    license = ("BSD-2-Clause, Apache-2.0")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "single_threaded": [True, False],
               "build_logging_server": [True, False],
               "with_iconv": [True, False],
               "working_locale": [True, False],
               "working_c_locale": [True, False],
               "decorated_name": [True, False],
               "unicode": [True, False],
               "thread_pool": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "single_threaded": False,
                       "build_logging_server": False,
                       "with_iconv": False,
                       "working_locale": False,
                       "working_c_locale": False,
                       "decorated_name": False,
                       "unicode": True,
                       "thread_pool": True}
    short_paths = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def requirements(self):
        if self.options.with_iconv:
            self.requires("libiconv/1.16")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LOG4CPLUS_ENABLE_THREAD_POOL"] = self.options.thread_pool
        self._cmake.definitions["UNICODE"] = self.options.unicode
        self._cmake.definitions["LOG4CPLUS_BUILD_TESTING"] = False
        self._cmake.definitions["WITH_UNIT_TESTS"] = False
        self._cmake.definitions["LOG4CPLUS_ENABLE_DECORATED_LIBRARY_NAME"] = self.options.decorated_name
        self._cmake.definitions["LOG4CPLUS_QT4"] = False
        self._cmake.definitions["LOG4CPLUS_QT5"] = False
        self._cmake.definitions["LOG4CPLUS_SINGLE_THREADED"] = self.options.single_threaded
        self._cmake.definitions["LOG4CPLUS_BUILD_LOGGINGSERVER"] = self.options.build_logging_server
        self._cmake.definitions["WITH_ICONV"] = self.options.with_iconv
        self._cmake.definitions["LOG4CPLUS_WORKING_LOCALE"] = self.options.working_locale
        self._cmake.definitions["LOG4CPLUS_WORKING_C_LOCALE"] = self.options.working_c_locale
        self._cmake.configure(build_dir=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        # don't force PIC
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set (CMAKE_POSITION_INDEPENDENT_CODE ON)", "")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.unicode:
            self.cpp_info.defines = ["UNICODE", "_UNICODE"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "m", "rt", "nsl"]
            if not self.options.single_threaded:
                self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["advapi32", "ws2_32"]
