import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file

required_conan_version = ">=1.53.0"


class EasyloggingppConan(ConanFile):
    name = "easyloggingpp"
    description = "Single-header C++ logging library."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/abumq/easyloggingpp"
    topics = ("logging", "stacktrace", "efficient-logging")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "enable_unicode": [True, False],
        "use_winsock2": [True, False],
        "force_use_std_thread": [True, False],
        "enable_crash_log": [True, False],
        "enable_thread_safe": [True, False],
        "enable_debug_assert_failure": [True, False],
        "enable_debug_errors": [True, False],
        "enable_default_logfile": [True, False],
        "enable_default_crash_handling": [True, False],
        "enable_fresh_logfile": [True, False],
        "disable_logs": [True, False],
        "disable_debug_logs": [True, False],
        "disable_info_logs": [True, False],
        "disable_warning_logs": [True, False],
        "disable_error_logs": [True, False],
        "disable_fatal_logs": [True, False],
        "disable_verbose_logs": [True, False],
        "disable_trace_logs": [True, False],
        "disable_log_to_file": [True, False],
        "disable_custom_format_specifiers": [True, False],
        "disable_logging_flags_from_arg": [True, False],
        "disable_log_file_from_arg": [True, False],
        "disable_check_macros": [True, False],
        "disable_debug_macros": [True, False],
        "disable_global_lock": [True, False],
        "lib_utc_datetime": [True, False],
    }
    default_options = {
        "fPIC": True,
        "enable_unicode": False,
        "use_winsock2": False,
        "force_use_std_thread": False,
        "enable_crash_log": False,
        "enable_thread_safe": False,
        "enable_debug_assert_failure": False,
        "enable_debug_errors": False,
        "enable_default_logfile": True,
        "enable_default_crash_handling": True,
        "enable_fresh_logfile": False,
        "disable_logs": False,
        "disable_debug_logs": False,
        "disable_info_logs": False,
        "disable_warning_logs": False,
        "disable_error_logs": False,
        "disable_fatal_logs": False,
        "disable_verbose_logs": False,
        "disable_trace_logs": False,
        "disable_log_to_file": False,
        "disable_custom_format_specifiers": False,
        "disable_logging_flags_from_arg": False,
        "disable_log_file_from_arg": False,
        "disable_check_macros": False,
        "disable_debug_macros": False,
        "disable_global_lock": False,
        "lib_utc_datetime": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _public_defines(self):
        defines = []
        if self.options.enable_unicode:
            defines.append("ELPP_UNICODE")
        if self.options.use_winsock2:
            defines.append("ELPP_WINSOCK2")
        if self.options.force_use_std_thread:
            defines.append("ELPP_FORCE_USE_STD_THREAD")
        if self.options.enable_crash_log:
            defines.append("ELPP_FEATURE_CRASH_LOG")
        if self.options.enable_thread_safe:
            defines.append("ELPP_THREAD_SAFE")
        if self.options.enable_debug_assert_failure:
            defines.append("ELPP_DEBUG_ASSERT_FAILURE")
        if self.options.enable_debug_errors:
            defines.append("ELPP_DEBUG_ERRORS")
        if not self.options.enable_default_logfile:
            defines.append("ELPP_NO_DEFAULT_LOG_FILE")
        if not self.options.enable_default_crash_handling:
            defines.append("ELPP_DISABLE_DEFAULT_CRASH_HANDLING")
        if self.options.enable_fresh_logfile:
            defines.append("ELPP_FRESH_LOG_FILE")
        if self.options.disable_logs:
            defines.append("ELPP_DISABLE_LOGS")
        if self.options.disable_debug_logs:
            defines.append("ELPP_DISABLE_DEBUG_LOGS")
        if self.options.disable_info_logs:
            defines.append("ELPP_DISABLE_INFO_LOGS")
        if self.options.disable_warning_logs:
            defines.append("ELPP_DISABLE_WARNING_LOGS")
        if self.options.disable_error_logs:
            defines.append("ELPP_DISABLE_ERROR_LOGS")
        if self.options.disable_fatal_logs:
            defines.append("ELPP_DISABLE_FATAL_LOGS")
        if self.options.disable_verbose_logs:
            defines.append("ELPP_DISABLE_VERBOSE_LOGS")
        if self.options.disable_trace_logs:
            defines.append("ELPP_DISABLE_TRACE_LOGS")
        if self.options.disable_log_to_file:
            defines.append("ELPP_NO_LOG_TO_FILE")
        if self.options.disable_custom_format_specifiers:
            defines.append("ELPP_DISABLE_CUSTOM_FORMAT_SPECIFIERS")
        if self.options.disable_logging_flags_from_arg:
            defines.append("ELPP_DISABLE_LOGGING_FLAGS_FROM_ARG")
        if self.options.disable_log_file_from_arg:
            defines.append("ELPP_DISABLE_LOG_FILE_FROM_ARG")
        if self.options.disable_check_macros:
            defines.append("ELPP_NO_CHECK_MACROS")
        if self.options.disable_debug_macros:
            defines.append("ELPP_NO_DEBUG_MACROS")
        if self.options.disable_global_lock:
            defines.append("ELPP_NO_GLOBAL_LOCK")
        if self.options.lib_utc_datetime:
            defines.append("ELPP_UTC_DATETIME")
        return defines

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["build_static_lib"] = True
        for d in self._public_defines:
            tc.preprocessor_definitions[d] = "1"
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set_property(TARGET easyloggingpp PROPERTY POSITION_INDEPENDENT_CODE ON)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = ["easyloggingpp"]
        self.cpp_info.defines = self._public_defines

        if self.options.enable_thread_safe and self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
