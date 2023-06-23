cmake_minimum_required(VERSION 3.2)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()
option(enable_crash_log "Enable crash log handler" OFF)
option(enable_thread_safe "Enable thread safety for use in multithreaded env" OFF)
option(enable_debug_errors "Enable debug errors in case of configuration issues" OFF)
option(enable_default_logfile "Enable creation of default logfile" ON)
option(disable_logs "Disables all logs" OFF)
option(disable_debug_logs "Disables debug logs" OFF)
option(disable_info_logs "Disables info logs" OFF)
option(disable_warning_logs "Disables warning logs" OFF)
option(disable_error_logs "Disables error logs" OFF)
option(disable_fatal_logs "Disables fatal logs" OFF)
option(disable_verbose_logs "Disables verbose logs" OFF)
option(disable_trace_logs "Disables trace logs" OFF)

if (enable_crash_log)
    add_definitions(-DELPP_FEATURE_CRASH_LOG)
endif()

if (enable_thread_safe)
    add_definitions(-DELPP_THREAD_SAFE)
endif()

if (enable_debug_errors)
    add_definitions(-DELPP_DEBUG_ERRORS)
endif()

if (NOT enable_default_logfile)
    add_definitions(-DELPP_NO_DEFAULT_LOG_FILE)
endif()

if (disable_logs)
    add_definitions(-DELPP_DISABLE_LOGS)
endif()

if (disable_debug_logs)
    add_definitions(-DELPP_DISABLE_DEBUG_LOGS)
endif()

if (disable_info_logs)
    add_definitions(-DELPP_DISABLE_INFO_LOGS)
endif()

if (disable_warning_logs)
    add_definitions(-DELPP_DISABLE_WARNING_LOGS)
endif()

if (disable_error_logs)
    add_definitions(-DELPP_DISABLE_ERROR_LOGS)
endif()

if (disable_fatal_logs)
    add_definitions(-DELPP_DISABLE_FATAL_LOGS)
endif()

if (disable_verbose_logs)
    add_definitions(-DELPP_DISABLE_VERBOSE_LOGS)
endif()

if (disable_trace_logs)
    add_definitions(-DELPP_DISABLE_TRACE_LOGS)
endif()

add_subdirectory("source_subfolder")
