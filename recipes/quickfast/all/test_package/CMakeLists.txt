cmake_minimum_required(VERSION 2.8.11)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test ${PROJECT_SOURCE_DIR}/main.cpp)

target_link_libraries(test ${CONAN_LIBS})
