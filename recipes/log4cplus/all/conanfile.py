import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class Log4cplusConan(ConanFile):
    name = "log4cplus"
    description = "simple to use C++ logging API, modelled after the Java log4j API"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/log4cplus/log4cplus"
    topics = ("conan", "log4cplus", "logging", "log", "logging-library")
    license = ("BSD-2-Clause, Apache-2.0")
    exports_sources = ["CMakeLists.txt"]
    generators = 'cmake'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False],
               "fPIC": [True, False],
               "single_threaded": [True, False],
               "build_logging_server": [True, False],
               "with_iconv": [True, False],
               "working_locale": [True, False],
               "working_c_locale": [True, False],
               "decorated_name": [True, False],
               "unicode": [True, False]}
    default_options = {'shared': False,
                       'fPIC': True,
                       'single_threaded': False,
                       'build_logging_server': False,
                       'with_iconv': False,
                       'working_locale': False,
                       'working_c_locale': False,
                       'decorated_name': False,
                       'unicode': True}
    short_paths = True
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def requirements(self):
        if self.options.with_iconv:
            self.requires.add('libiconv/1.16')

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        archive_name = self.name + "-" + self.version
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(archive_name, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['UNICODE'] = self.options.unicode
        cmake.definitions['LOG4CPLUS_BUILD_TESTING'] = False
        cmake.definitions['WITH_UNIT_TESTS'] = False
        cmake.definitions["LOG4CPLUS_ENABLE_DECORATED_LIBRARY_NAME"] = self.options.decorated_name
        cmake.definitions['LOG4CPLUS_QT4'] = False
        cmake.definitions['LOG4CPLUS_QT5'] = False
        cmake.definitions['LOG4CPLUS_SINGLE_THREADED'] = self.options.single_threaded
        cmake.definitions['LOG4CPLUS_BUILD_LOGGINGSERVER'] = self.options.build_logging_server
        cmake.definitions['WITH_ICONV'] = self.options.with_iconv
        cmake.definitions['LOG4CPLUS_WORKING_LOCALE'] = self.options.working_locale
        cmake.definitions['LOG4CPLUS_WORKING_C_LOCALE'] = self.options.working_c_locale
        cmake.configure(build_dir=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ['Ws2_32']
