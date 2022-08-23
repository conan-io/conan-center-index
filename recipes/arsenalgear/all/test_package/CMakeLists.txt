cmake_minimum_required(VERSION 3.1)

project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(arsenalgear REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} arsenalgear::arsenalgear)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
