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
    exports_sources = ["patches/*"]
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "use_system_tz_db": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "use_system_tz_db": False}

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_DATE_TESTING"] = False
        cmake.definitions["USE_SYSTEM_TZ_DB"] = self.options.use_system_tz_db
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def requirements(self):
        if self.options.use_system_tz_db == False:
            self.requires("libcurl/7.67.0")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if tools.os_info.is_linux:
            self.cpp_info.libs.append("pthread")
