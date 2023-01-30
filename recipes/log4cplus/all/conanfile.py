from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file, collect_libs
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os

required_conan_version = ">=1.53.0"

class Log4cplusConan(ConanFile):
    name = "log4cplus"
    description = "simple to use C++ logging API, modelled after the Java log4j API"
    license = ("BSD-2-Clause, Apache-2.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/log4cplus/log4cplus"
    topics = ("logging", "log", "logging-library")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "single_threaded": [True, False],
        "build_logging_server": [True, False],
        "with_iconv": [True, False],
        "working_locale": [True, False],
        "working_c_locale": [True, False],
        "decorated_name": [True, False],
        "unicode": [True, False],
        "thread_pool": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "single_threaded": False,
        "build_logging_server": False,
        "with_iconv": False,
        "working_locale": False,
        "working_c_locale": False,
        "decorated_name": False,
        "unicode": True,
        "thread_pool": True,
    }
    short_paths = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_iconv:
            self.requires("libiconv/1.17")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LOG4CPLUS_ENABLE_THREAD_POOL"] = self.options.thread_pool
        tc.variables["UNICODE"] = self.options.unicode
        tc.variables["LOG4CPLUS_BUILD_TESTING"] = False
        tc.variables["WITH_UNIT_TESTS"] = False
        tc.variables["LOG4CPLUS_ENABLE_DECORATED_LIBRARY_NAME"] = self.options.decorated_name
        tc.variables["LOG4CPLUS_QT4"] = False
        tc.variables["LOG4CPLUS_QT5"] = False
        tc.variables["LOG4CPLUS_SINGLE_THREADED"] = self.options.single_threaded
        tc.variables["LOG4CPLUS_BUILD_LOGGINGSERVER"] = self.options.build_logging_server
        tc.variables["WITH_ICONV"] = self.options.with_iconv
        tc.variables["LOG4CPLUS_WORKING_LOCALE"] = self.options.working_locale
        tc.variables["LOG4CPLUS_WORKING_C_LOCALE"] = self.options.working_c_locale
        tc.generate()

        dpes = CMakeDeps(self)
        dpes.generate()

    def _patch_sources(self):
        # don't force PIC
        replace_in_file(self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "set (CMAKE_POSITION_INDEPENDENT_CODE ON)",
            ""
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.options.unicode:
            self.cpp_info.defines = ["UNICODE", "_UNICODE"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "m", "rt"]
            if not self.options.single_threaded:
                self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["advapi32", "ws2_32"]
