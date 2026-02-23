cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(libtomcrypt CONFIG REQUIRED)

add_executable(example src/example.c)
target_link_libraries(example PRIVATE libtomcrypt::libtomcrypt)
