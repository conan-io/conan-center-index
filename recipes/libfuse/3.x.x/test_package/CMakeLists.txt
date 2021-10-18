cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(libfuse REQUIRED)

add_executable(${CMAKE_PROJECT_NAME} test_package.c)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE libfuse::libfuse)
target_compile_definitions(${PROJECT_NAME} PRIVATE FUSE_USE_VERSION=34)
