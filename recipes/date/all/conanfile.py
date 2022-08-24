from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.33.0"


class DateConan(ConanFile):
    name = "date"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/HowardHinnant/date"
    description = "A date and time library based on the C++11/14/17 <chrono> header"
    topics = ("date", "datetime", "timezone",
              "calendar", "time", "iana-database")
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
        "use_system_tz_db": [True, False],
        "use_tz_db_in_dot": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
        "use_system_tz_db": False,
        "use_tz_db_in_dot": False,
    }

    exports_sources = ["patches/*", "CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os in ["iOS", "tvOS", "watchOS"]:
            self.options.use_system_tz_db = True

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if not self.options.header_only and not self.options.use_system_tz_db:
            self.requires("libcurl/7.78.0")

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, "11")

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = CMake(self)
        cmake.definitions["ENABLE_DATE_TESTING"] = False
        cmake.definitions["USE_SYSTEM_TZ_DB"] = self.options.use_system_tz_db
        cmake.definitions["USE_TZ_DB_IN_DOT"] = self.options.use_tz_db_in_dot
        cmake.definitions["BUILD_TZ_LIB"] = not self.options.header_only
        # workaround for clang 5 not having string_view
        if tools.scm.Version(self, self.version) >= "3.0.0" and self.settings.compiler == "clang" \
                and tools.scm.Version(self, self.settings.compiler.version) <= "5.0":
            cmake.definitions["DISABLE_STRING_VIEW"] = True
        cmake.configure()

        self._cmake = cmake
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        if not self.options.header_only:
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
        else:
            cmake = self._configure_cmake()
            cmake.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "CMake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "date"
        self.cpp_info.names["cmake_find_package_multi"] = "date"

        # date-tz
        if not self.options.header_only:
            self.cpp_info.components["date-tz"].names["cmake_find_package"] = "date-tz"
            self.cpp_info.components["date-tz"].names["cmake_find_package_multi"] = "date-tz"
            lib_name = "{}tz".format("date-" if tools.scm.Version(self, self.version) >= "3.0.0" else "")
            self.cpp_info.components["date-tz"].libs = [lib_name]
            if self.settings.os == "Linux":
                self.cpp_info.components["date-tz"].system_libs.append("pthread")

            if not self.options.use_system_tz_db:
                self.cpp_info.components["date-tz"].requires.append("libcurl::libcurl")

            if self.options.use_system_tz_db and not self.settings.os == "Windows":
                use_os_tzdb = 1
            else:
                use_os_tzdb = 0

            defines = ["USE_OS_TZDB={}".format(use_os_tzdb)]
            if self.settings.os == "Windows" and self.options.shared:
                defines.append("DATE_USE_DLL=1")

            self.cpp_info.components["date-tz"].defines.extend(defines)
