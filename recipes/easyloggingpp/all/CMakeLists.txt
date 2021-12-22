cmake_minimum_required(VERSION 3.2)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()
option(enable_crash_log "Enable crash log handler" OFF)
option(enable_thread_safe "Enable thread safety for use in multithreaded env" OFF)
option(enable_debug_errors "Enable debug errors in case of configuration issues" OFF)
option(enable_default_logfile "Enable creation of default logfile" ON)

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

add_subdirectory("source_subfolder")
