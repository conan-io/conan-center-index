from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import download, get, rmdir, apply_conandata_patches, export_conandata_patches, copy
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
        "tz_db": ["embedded", "system", "manual"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
        "tz_db": "embedded"
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
            self.package_type = "header-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["tzdatabase"], destination="tzdata", strip_root=True)
        download(self, **self.conan_data["sources"][self.version]["windows_zones"], filename=os.path.join("tzdata", "windowsZones.xml"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ENABLE_DATE_TESTING"] = False
        tc.cache_variables["USE_SYSTEM_TZ_DB"] = bool(self.options.tz_db == "system")
        tc.cache_variables["MANUAL_TZ_DB"] = bool(self.options.tz_db in ["embedded", "manual"])
        tc.cache_variables["BUILD_TZ_LIB"] = not self.options.header_only
        if self.options.tz_db == "embedded":
            tc.preprocessor_definitions["INSTALL"] = self.source_folder.replace("\\", "/")
        # workaround for gcc 7 and clang 5 not having string_view
        if Version(self.version) >= "3.0.0" and \
            ((self.settings.compiler == "gcc" and Version(self.settings.compiler.version) <= "7.0") or \
             (self.settings.compiler == "clang" and Version(self.settings.compiler.version) <= "5.0")):
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

        # date-tz
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

            use_os_tzdb = 1 if self.options.tz_db == "system" and not self.settings.os == "Windows" else 0
            defines = [f"USE_OS_TZDB={use_os_tzdb}"]
            if self.settings.os == "Windows" and self.options.shared:
                defines.append("DATE_BUILD_DLL=1")

            if Version(self.version) >= "3.0.0" and \
                ((self.settings.compiler == "gcc" and Version(self.settings.compiler.version) <= "7.0") or \
                (self.settings.compiler == "clang" and Version(self.settings.compiler.version) <= "5.0")):
                defines.append("HAS_STRING_VIEW=0")
            else:
                defines.append("HAS_STRING_VIEW=1")

            self.cpp_info.components["date-tz"].defines.extend(defines)
