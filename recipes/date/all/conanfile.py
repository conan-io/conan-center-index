from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
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
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
        "use_system_tz_db": ["deprecated", True, False],
        "tz_db": ["download", "system", "manual"],
        "use_tz_db_in_dot": [True, False]
    }
    options_description = {
        "tz_db": """Select how to consume the tz database.
                    - download: The latest database is downloaded in runtime using curl.
                    - system: Use the system database.
                    - manual: The consumer should indicate the path to the database with set_install()""",
        "use_tz_db_in_dot": "Download the tz database in the current folder"
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
        "use_system_tz_db": "deprecated",
        "tz_db": "download",
        "use_tz_db_in_dot": False
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os in ["iOS", "tvOS", "watchOS", "Android"]:
            self.options.tz_db = "system"

    def configure(self):
        if self.options.shared or self.options.header_only:
            self.options.rm_safe("fPIC")
        if self.options.header_only:
            del self.options.shared
            del self.options.tz_db
            del self.options.use_tz_db_in_dot
            self.package_type = "header-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        del self.info.options.use_system_tz_db
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        if self.options.use_system_tz_db != "deprecated":
            self.output.warning(f"The '{self.ref}/*:use_system_tz_db' option is deprecated. Use '{self.ref}/*:tz_db=system' instead.")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.options.get_safe("tz_db") == "system" and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Using system tz database is not supported on Windows")
        if self.options.get_safe("tz_db") != "download" and self.options.get_safe("use_tz_db_in_dot"):
            raise ConanInvalidConfiguration("Option 'use_tz_db_in_dot'=True cannot be used with 'tz_db' != 'download'")

    def requirements(self):
        if self.version == "2.4.1" or self.options.get_safe("tz_db") == "download":
            self.requires("libcurl/[>=7.78 <9]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ENABLE_DATE_TESTING"] = False
        if self.options.header_only:
            tc.cache_variables["BUILD_TZ_LIB"] = False
        else:
            tc.cache_variables["USE_SYSTEM_TZ_DB"] = bool(self.options.tz_db == "system")
            tc.cache_variables["MANUAL_TZ_DB"] = bool(self.options.tz_db == "manual")
            tc.cache_variables["USE_TZ_DB_IN_DOT"] = self.options.use_tz_db_in_dot
            tc.cache_variables["BUILD_TZ_LIB"] = True
            if self.options.get_safe("use_tz_db_in_dot"):
                tc.preprocessor_definitions["INSTALL"] = "."
        if Version(self.version) < 3:
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
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
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "CMake"))
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include", "date"),
             src=os.path.join(self.source_folder, "include", "date"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "date")
        self.cpp_info.set_property("cmake_target_name", "date::date")

        if self.options.header_only:
            self.cpp_info.bindirs = []
            self.cpp_info.defines.append("DATE_HEADER_ONLY")
            self.cpp_info.libdirs = []
        else:
            self.cpp_info.components["date-tz"].set_property("cmake_target_name", "date::date-tz")
            lib_name = "{}tz".format("date-" if Version(self.version) >= "3.0.0" else "")
            self.cpp_info.components["date-tz"].libs = [lib_name]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["date-tz"].system_libs.extend(["m", "pthread"])

            defines = []
            if self.options.tz_db == "system":
                defines.append("USE_OS_TZDB=1")

            if self.settings.os == "Windows" and self.options.shared:
                defines.append("DATE_BUILD_DLL=1")

            self.cpp_info.components["date-tz"].defines.extend(defines)

            if self.version == "2.4.1" or self.options.get_safe("tz_db") == "download":
                self.cpp_info.components["date-tz"].requires.append("libcurl::libcurl")
