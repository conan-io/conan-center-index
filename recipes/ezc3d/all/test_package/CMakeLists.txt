cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(ezc3d REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ezc3d::ezc3d) # TODO: remove ezc3d namespace when fixed in conanfile
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
