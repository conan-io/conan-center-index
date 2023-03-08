cmake_minimum_required(VERSION 3.15)

project(test_package CXX) # if the project uses c++
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(async_simple REQUIRED CONFIG)

# Re-use the same source file from test_package folder
add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package
target_link_libraries(${PROJECT_NAME} PRIVATE async_simple::async_simple_header_only)
