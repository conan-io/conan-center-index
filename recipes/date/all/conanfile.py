import os
from conans import ConanFile, CMake, tools


class DateConan(ConanFile):
    name = "date"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/HowardHinnant/date"
    description = "A date and time library based on the C++11/14/17 <chrono> header"
    topics = ("date", "datetime", "timezone",
              "calendar", "time", "iana-database")
    license = "MIT"
    exports_sources = ["patches/*", "CMakeLists.txt"]
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "use_system_tz_db": [True, False],
               "use_tz_db_in_dot": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "use_system_tz_db": True,
                       "use_tz_db_in_dot": False}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        #requires at least c++11 to work.
        tools.check_min_cppstd(self, "11")

        if self.settings.os == "Windows":
            del self.options.use_system_tz_db
            del self.options.use_tz_db_in_dot

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_DATE_TESTING"] = False
        if not self.settings.os == "Windows":
            cmake.definitions["USE_TZ_DB_IN_DOT"] = self.options.use_tz_db_in_dot
            cmake.definitions["USE_SYSTEM_TZ_DB"] = self.options.use_system_tz_db

        cmake.configure()
        return cmake

    def requirements(self):
        if self.settings.os == "Windows" or not self.options.use_system_tz_db:
            self.requires("libcurl/7.67.0")

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "CMake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if self.settings.os == "Windows":
            use_system_tz_db = 0
        else:
            use_system_tz_db = 0 if self.options.use_system_tz_db else 1
        defines = ["USE_AUTOLOAD={}".format(use_system_tz_db),
                   "HAS_REMOTE_API={}".format(use_system_tz_db)]
        if self.options.shared:
            defines.append("DATE_USE_DLL=1")
        self.cpp_info.defines.extend(defines)
