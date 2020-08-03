cmake_minimum_required(VERSION 3.3)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Threads)

add_executable(seasocks_test seasocks_test.cpp)
target_link_libraries(seasocks_test ${CONAN_LIBS} ${CMAKE_THREAD_LIBS_INIT})
