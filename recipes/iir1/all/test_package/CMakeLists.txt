cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(iir REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

if(TARGET iir::iir)
    target_link_libraries(${PROJECT_NAME} PRIVATE iir::iir)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE iir::iir_static)
endif()
