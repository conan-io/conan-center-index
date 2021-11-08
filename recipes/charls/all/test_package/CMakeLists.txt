cmake_minimum_required(VERSION 3.1.3)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(charls CONFIG REQUIRED)

add_executable(test_package_c test_package.c)
target_link_libraries(test_package_c charls)
set_target_properties(test_package_c PROPERTIES LINKER_LANGUAGE CXX)

add_executable(test_package_cpp test_package.cpp)
target_link_libraries(test_package_cpp charls)
set_target_properties(test_package_cpp PROPERTIES CXX_STANDARD 14)
