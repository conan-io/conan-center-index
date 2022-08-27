cmake_minimum_required(VERSION 3.13)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(sdbus-c++ REQUIRED)

add_executable(example ../test_package/example.cpp)
target_link_libraries(example SDBusCpp::sdbus-c++)
