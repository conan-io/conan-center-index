cmake_minimum_required(VERSION 3.0)
project(test_package C)

find_package(ZLIB REQUIRED)

add_executable(test_zlib test.c)
target_link_libraries(test_zlib ZLIB::ZLIB)
set_target_properties(test_zlib PROPERTIES OUTPUT_NAME "test")
