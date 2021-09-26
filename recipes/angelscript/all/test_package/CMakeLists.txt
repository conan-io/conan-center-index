cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)


find_package(Angelscript REQUIRED CONFIG)

add_executable(example
    example.cpp
)

target_link_libraries(example
    PRIVATE
    Angelscript::angelscript
)
