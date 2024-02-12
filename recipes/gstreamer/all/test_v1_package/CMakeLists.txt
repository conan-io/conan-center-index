cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(gstreamer REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE
    gstreamer::gstreamer-1.0 gstreamer::gstreamer-base-1.0 gstreamer::gstreamer-controller-1.0
    gstreamer::gstreamer-net-1.0 gstreamer::gstreamer-check-1.0)
if (TARGET gstreamer::gstcoreelements)
    target_link_libraries(${PROJECT_NAME} PRIVATE gstreamer::gstcoreelements)
endif ()
