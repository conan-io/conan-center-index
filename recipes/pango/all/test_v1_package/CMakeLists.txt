cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(pango CONFIG REQUIRED)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE pango::pango)
