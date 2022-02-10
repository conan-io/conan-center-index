cmake_minimum_required(VERSION 3.5)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(AWSSDK REQUIRED)
add_library(aws-cpp-sdk-core ALIAS AWS::aws-sdk-cpp-core)

add_subdirectory(source_subfolder/aws-cpp-sdk-cdi)
