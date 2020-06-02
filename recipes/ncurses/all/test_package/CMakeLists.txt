cmake_minimum_required(VERSION 3.0)
project(test_package)

set(CMAKE_VERBOSE_MAKEFILE ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
set_property(TARGET ${PROJECT_NAME} PROPERTY LINKER_LANGUAGE CXX)
