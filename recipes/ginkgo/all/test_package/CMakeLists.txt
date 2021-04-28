cmake_minimum_required(VERSION 3.1)
project(test_install)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Ginkgo REQUIRED CONFIG)

add_executable(test_install test_install.cpp)
target_link_libraries(test_install Ginkgo::ginkgo)
set_target_properties(test_install PROPERTIES CXX_STANDARD 14)
