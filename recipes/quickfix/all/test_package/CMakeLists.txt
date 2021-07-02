cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(executor ${PROJECT_SOURCE_DIR}/executor.cpp)
target_link_libraries(executor ${CONAN_LIBS})
