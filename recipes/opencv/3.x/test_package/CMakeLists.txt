cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(OpenCV REQUIRED core imgproc CONFIG)

option(built_contrib "Enabled if opencv is built contrib sfm" OFF)
if(built_contrib)
    add_definitions(-DBUILT_CONTRIB)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} opencv_core opencv_imgproc $<TARGET_NAME_IF_EXISTS:opencv_sfm>)
