cmake_minimum_required(VERSION 3.1)
project(test_package)

set(CMAKE_CXX_STANDARD 11)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(co REQUIRED)

add_executable(${PROJECT_NAME} test_package.cc)
target_link_libraries(${PROJECT_NAME} co::co)
