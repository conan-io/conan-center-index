cmake_minimum_required(VERSION 3.1.0)

set(CMAKE_CXX_STANDARD 17)

project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_set_vs_runtime()
conan_set_libcxx()
conan_output_dirs_setup()

find_package(Qt6 REQUIRED CONFIG)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

add_executable(${PROJECT_NAME} test_package.cpp greeter.h example.qrc)

target_link_libraries(${PROJECT_NAME} Qt6::Core)
