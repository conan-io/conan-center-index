cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test ${PROJECT_SOURCE_DIR}/main.cpp)

target_link_libraries(test ${CONAN_LIBS})

set_property(TARGET test PROPERTY CXX_STANDARD 11)
