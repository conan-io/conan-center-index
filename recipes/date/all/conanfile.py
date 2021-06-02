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
               "header_only": [True, False],
               "use_system_tz_db": [True, False],
               "use_tz_db_in_dot": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "header_only": False,
                       "use_system_tz_db": False,
                       "use_tz_db_in_dot": False}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = CMake(self)
        cmake.definitions["ENABLE_DATE_TESTING"] = False
        cmake.definitions["USE_SYSTEM_TZ_DB"] = self.options.use_system_tz_db
        cmake.definitions["USE_TZ_DB_IN_DOT"] = self.options.use_tz_db_in_dot
        cmake.definitions["BUILD_TZ_LIB"] = not self.options.header_only
        # workaround for clang 5 not having string_view
        if tools.Version(self.version) >= "3.0.0" and self.settings.compiler == "clang" \
                and tools.Version(self.settings.compiler.version) <= "5.0":
            cmake.definitions["DISABLE_STRING_VIEW"] = True
        cmake.configure()

        self._cmake = cmake
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def requirements(self):
        if self.options.header_only:
            return
        if not self.options.use_system_tz_db:
            self.requires("libcurl/7.69.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self.options.header_only:
            self.output.info("Header only package, skipping build")
            return
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses",
                  src=self._source_subfolder)
        if self.options.header_only:
            src = os.path.join(self._source_subfolder, "include", "date")
            dst = os.path.join("include", "date")
            self.copy(pattern="date.h", dst=dst, src=src)
            self.copy(pattern="tz.h", dst=dst, src=src)
            self.copy(pattern="ptz.h", dst=dst, src=src)
            self.copy(pattern="iso_week.h", dst=dst, src=src)
            self.copy(pattern="julian.h", dst=dst, src=src)
            self.copy(pattern="islamic.h", dst=dst, src=src)
            return

        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "CMake"))

    def package_info(self):
        if self.options.header_only:
            return

        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")

        if self.options.use_system_tz_db and not self.settings.os == "Windows":
            use_os_tzdb = 1
        else:
            use_os_tzdb = 0

        defines = ["USE_OS_TZDB={}".format(use_os_tzdb)]
        if self.settings.os == "Windows" and self.options.shared:
            defines.append("DATE_USE_DLL=1")

        self.cpp_info.defines.extend(defines)

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()
