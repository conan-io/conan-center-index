cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(easyexif REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE easyexif::easyexif)
