cmake_minimum_required(VERSION 3.5)

project(EXAMPLE)

find_package(angelscript REQUIRED)

add_executable(example
    example.cpp
)

target_link_libraries(example
    PRIVATE
    Angelscript::angelscript
)
