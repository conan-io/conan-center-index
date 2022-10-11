cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(antlr4-runtime REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
if(TARGET antlr4_shared)
    target_link_libraries(${PROJECT_NAME} PRIVATE antlr4_shared)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE antlr4_static)
endif()
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
