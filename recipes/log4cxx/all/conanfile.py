import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=1.53.0"


class Log4cxxConan(ConanFile):
    name = "log4cxx"
    description = "Logging framework for C++ patterned after Apache log4j"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://logging.apache.org/log4cxx"
    topics = ("logging", "log")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "char_type": ["utf-8", "wchar_t", "unichar"],
        "char_encoding": ["utf-8", "locale"],
        "with_networking": [True, False],
        "with_wchar_t": [True, False],
        "with_fmt_layout": [True, False],
        "with_odbc_appender": [True, False],
        "with_multiprocess_rolling_file_appender": [True, False],
        "with_smtp_appender": [True, False],
        "with_qt": [True, False],
    }
    options_description = {
        "char_type": "The log4cxx internal character type (selects the std::basic_string template parameter used by log4cxx::LogString)",
        "char_encoding": "The external character set used when writing to files",
        "with_networking": "Include appenders that use network i/o",
        "with_wchar_t": "Include wchar_t API methods in class interfaces",
        "with_fmt_layout": "Include the log4cxx::FMTLayout class that uses libfmt to layout messages",
        "with_odbc_appender": "Include the log4cxx::ODBCAppender that sends log events to a database",
        "with_multiprocess_rolling_file_appender": "Include the appender that allows multiple applications to log to the same file",
        "with_smtp_appender": "Include the appender that sends an e-mail when a specific logging event occurs",
        "with_qt": "Allow QString values in the LOG4CXX_WARN, LOG4CXX_INFO, LOG4CXX_DEBUG etc. macros",
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "char_type": "utf-8",
        "char_encoding": "utf-8",
        "with_networking": True,
        "with_wchar_t": False,
        "with_fmt_layout": False,
        "with_odbc_appender": False,
        "with_multiprocess_rolling_file_appender": False,
        "with_smtp_appender": False,
        "with_qt": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
            self.options.rm_safe("with_smtp_appender") # *nix only

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("apr/1.7.4")
        self.requires("apr-util/1.6.1")
        self.requires("expat/2.6.4")
        if self.options.get_safe("with_odbc_appender") and self.settings.os != "Windows":
            self.requires("odbc/2.3.11")
        if self.options.get_safe("with_smtp_appender"):
            self.requires("libesmtp/1.1.0")
        if self.options.get_safe("with_fmt_layout"):
            self.requires("fmt/10.2.1")
        if self.options.get_safe("with_qt"):
            self.requires("qt/[~5.15]")

    def validate(self):
        if self.options.get_safe("with_multiprocess_rolling_file_appender"):
            # TODO: if compiler doesn't support C++17, boost can be used instead
            self.output.info("multiprocess rolling file appender requires C++17.")
            check_min_cppstd(self, "17")

    def build_requirements(self):
        if self.settings.os != "Windows":
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["LOG4CXX_INSTALL_PDB"] = False
        tc.variables["LOG4CXX_NETWORKING_SUPPORT"] = self.options.with_networking
        tc.variables["LOG4CXX_MULTIPROCESS_ROLLING_FILE_APPENDER"] = self.options.with_multiprocess_rolling_file_appender
        tc.variables["ENABLE_FMT_LAYOUT"] = self.options.with_fmt_layout
        if self.settings.os != "Windows":
            tc.variables["LOG4CXX_ENABLE_ESMTP"] = self.options.with_smtp_appender
        tc.variables["LOG4CXX_ENABLE_ODBC"] = self.options.with_odbc_appender
        tc.variables["LOG4CXX_CHAR"] = self.options.char_type
        tc.variables["LOG4CXX_CHARSET"] = self.options.char_encoding
        tc.variables["LOG4CXX_WCHAR_T"] = self.options.with_wchar_t
        tc.variables["LOG4CXX_QT_SUPPORT"] = self.options.with_qt
        tc.variables["APR_STATIC"] = not self.dependencies["apr"].options.shared
        tc.variables["APU_STATIC"] = not self.dependencies["apr-util"].options.shared
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("apr", "cmake_file_name", "APR")
        deps.set_property("apr-util", "cmake_file_name", "APR-Util")
        deps.set_property("apr-util", "cmake_additional_variables_prefixes", ["APR_UTIL"])
        deps.set_property("expat", "cmake_file_name", "EXPAT")
        deps.set_property("expat", "cmake_find_mode", "config")
        deps.set_property("expat", "cmake_target_name", "EXPAT::EXPAT")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "NOTICE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "log4cxx")
        self.cpp_info.set_property("cmake_target_name", "log4cxx")
        self.cpp_info.set_property("pkg_config_name", "liblog4cxx")

        if not self.options.shared:
            self.cpp_info.defines = ["LOG4CXX_STATIC"]
        self.cpp_info.libs = ["log4cxx"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["odbc32"]
