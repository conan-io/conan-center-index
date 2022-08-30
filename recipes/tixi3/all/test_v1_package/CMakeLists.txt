cmake_minimum_required(VERSION 3.1.2)
project(tixi3_conan_test CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(tixi3 REQUIRED CONFIG)

add_executable(tixi3_conan_test ../test_package/main.cpp)
target_link_libraries(tixi3_conan_test tixi3)
