cmake_minimum_required(VERSION 3.12)
project(netlink_example)

find_package(Threads REQUIRED)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(show_links show_links.c)
target_link_libraries(show_links ${CONAN_LIBS} Threads::Threads)
