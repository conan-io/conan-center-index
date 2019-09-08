cmake_minimum_required(VERSION 3.1.2)
project(test_package CXX)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if(WITH_MAIN)
    add_executable(${PROJECT_NAME} test_package.cpp)
else()
    add_executable(${PROJECT_NAME} main.cpp test_package.cpp)
endif()

target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
if(WITH_GMOCK)
    target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_GMOCK)
endif()
