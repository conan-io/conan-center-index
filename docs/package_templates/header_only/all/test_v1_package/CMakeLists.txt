cmake_minimum_required(VERSION 3.8)

project(test_package C) # if the project is pure C
project(test_package CXX) # if the project uses c++

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(package REQUIRED CONFIG)

# Re-use the same source file from test_package folder
add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package
target_link_libraries(${PROJECT_NAME} PRIVATE package::package)
# in case the target project requires a C++ standard
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
