cmake_minimum_required(VERSION 3.3)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Seasocks REQUIRED)
find_package(Threads REQUIRED)

add_executable(seasocks_test seasocks_test.cpp)
target_link_libraries(seasocks_test PRIVATE Seasocks::seasocks Threads::Threads)
set_property(TARGET seasocks_test PROPERTY CXX_STANDARD 11)
