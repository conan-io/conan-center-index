from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, rmdir, apply_conandata_patches, export_conandata_patches, copy
from conan.tools.scm import Version

import os

required_conan_version = ">=1.53.0"


class DateConan(ConanFile):
    name = "date"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/HowardHinnant/date"
    description = "A date and time library based on the C++11/14/17 <chrono> header"
    topics = ("datetime", "timezone", "calendar", "time", "iana-database")
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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os in ["iOS", "tvOS", "watchOS", "Android"]:
            self.options.use_system_tz_db = True

    def configure(self):
        if self.options.shared or self.options.header_only:
            self.options.rm_safe("fPIC")
        if self.options.header_only:
            del self.options.shared

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if not self.options.header_only and not self.options.use_system_tz_db:
            self.requires("libcurl/8.2.1")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_DATE_TESTING"] = False
        tc.variables["USE_SYSTEM_TZ_DB"] = self.options.use_system_tz_db
        tc.variables["USE_TZ_DB_IN_DOT"] = self.options.use_tz_db_in_dot
        tc.variables["BUILD_TZ_LIB"] = not self.options.header_only
        # workaround for clang 5 not having string_view
        if Version(self.version) >= "3.0.0" and self.settings.compiler == "clang" \
                and Version(self.settings.compiler.version) <= "5.0":
            tc.cache_variables["DISABLE_STRING_VIEW"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.options.header_only:
            src = os.path.join(self.source_folder, "include", "date")
            dst = os.path.join(self.package_folder, "include", "date")
            copy(self, "date.h", dst=dst, src=src)
            copy(self, "tz.h", dst=dst, src=src)
            copy(self, "ptz.h", dst=dst, src=src)
            copy(self, "iso_week.h", dst=dst, src=src)
            copy(self, "julian.h", dst=dst, src=src)
            copy(self, "islamic.h", dst=dst, src=src)
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "CMake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "date::date")
        # TODO: Remove legacy .names attribute when conan 2.0 is released
        self.cpp_info.names["cmake_find_package"] = "date"
        self.cpp_info.names["cmake_find_package_multi"] = "date"

        # date-tz
        if not self.options.header_only:
            self.cpp_info.components["date-tz"].set_property("cmake_target_name", "date::date-tz")
            # TODO: Remove legacy .names attribute when conan 2.0 is released
            self.cpp_info.components["date-tz"].names["cmake_find_package"] = "date-tz"
            self.cpp_info.components["date-tz"].names["cmake_find_package_multi"] = "date-tz"
            lib_name = "{}tz".format("date-" if Version(self.version) >= "3.0.0" else "")
            self.cpp_info.components["date-tz"].libs = [lib_name]
            if self.settings.os == "Linux":
                self.cpp_info.components["date-tz"].system_libs.append("pthread")
                self.cpp_info.components["date-tz"].system_libs.append("m")

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
        else:
            self.cpp_info.defines.append("DATE_HEADER_ONLY")
            self.cpp_info.libdirs = []
