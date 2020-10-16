cmake_minimum_required(VERSION 3.10.2)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(IGN_MATH_MAJOR_VER 6)

find_package(ignition-math${IGN_MATH_MAJOR_VER} REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ignition-math${IGN_MATH_MAJOR_VER}::ignition-math${IGN_MATH_MAJOR_VER})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
