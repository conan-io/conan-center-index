cmake_minimum_required(VERSION 3.10)
project(cmake_wrapper C)

include(conanbuildinfo.cmake)
conan_basic_setup()

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

option(BUILD_SHARED_LIBS "Build shared libraries by default")

if(WIN32)
    include(cmake/packetntx.cmake)
endif()

include(cmake/winpcap.cmake)
