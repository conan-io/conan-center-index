cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(gstreamer REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)

if (CMAKE_SYSTEM_NAME STREQUAL "Windows")
    target_link_libraries(${PROJECT_NAME} PRIVATE
        gstreamer::gstreamer-1.0 gstreamer::gstreamer-base-1.0 gstreamer::gstreamer-controller-1.0
        gstreamer::gstreamer-net-1.0 gstreamer::gstreamer-check-1.0)
    if (TARGET gstreamer::gstcoreelements)
        target_link_libraries(${PROJECT_NAME} PRIVATE gstreamer::gstcoreelements)
    endif ()
else()
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(gstreamer-1.0 REQUIRED IMPORTED_TARGET gstreamer-1.0)
    pkg_check_modules(gstreamer-base-1.0 REQUIRED IMPORTED_TARGET gstreamer-base-1.0)
    pkg_check_modules(gstreamer-controller-1.0 REQUIRED IMPORTED_TARGET gstreamer-controller-1.0)
    pkg_check_modules(gstreamer-net-1.0 REQUIRED IMPORTED_TARGET gstreamer-net-1.0)
    pkg_check_modules(gstreamer-check-1.0 REQUIRED IMPORTED_TARGET gstreamer-check-1.0)
    pkg_check_modules(gstcoreelements IMPORTED_TARGET gstcoreelements)
    target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::gstreamer-1.0 PkgConfig::gstreamer-base-1.0 PkgConfig::gstreamer-controller-1.0
        PkgConfig::gstreamer-net-1.0 PkgConfig::gstreamer-check-1.0)
    if (TARGET PkgConfig::gstcoreelements)
        target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::gstcoreelements)
    endif ()
endif()
