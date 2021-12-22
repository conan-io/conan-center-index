cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(AWSSDK REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example AWS::aws-sdk-cpp-s3)
