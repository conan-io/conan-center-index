cmake_minimum_required(VERSION 3.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(magic_enum REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
target_link_libraries(${PROJECT_NAME} magic_enum::magic_enum)
