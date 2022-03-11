cmake_minimum_required(VERSION 3.1)

project(args-parser.test)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)

conan_basic_setup(TARGETS)

find_package(args-parser REQUIRED)

add_executable(${PROJECT_NAME} example.cpp)

target_link_libraries(${PROJECT_NAME} args-parser::args-parser)

set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 14
    CXX_STANDARD_REQUIRED ON
)
