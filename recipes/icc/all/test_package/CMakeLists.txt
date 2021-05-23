cmake_minimum_required(VERSION 3.17)
project(PackageTest)

set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(icc REQUIRED)

add_executable(example example.cpp)
target_include_directories(example PUBLIC ${CONAN_INCLUDE_DIRS_ICC})
target_link_libraries(example icc::icc)
