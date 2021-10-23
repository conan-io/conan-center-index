cmake_minimum_required(VERSION 3.2)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()
option(enable_crash_log "Enable crash log handler" OFF)
option(enable_thread_safe "Enable thread safety for use in multithreaded env" OFF)

if (enable_crash_log)
    add_definitions(-DELPP_FEATURE_CRASH_LOG)
endif()

if (enable_thread_safe)
    add_definitions(-DELPP_THREAD_SAFE)
endif()

add_subdirectory("source_subfolder")
