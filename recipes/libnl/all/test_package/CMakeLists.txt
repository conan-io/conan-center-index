cmake_minimum_required(VERSION 3.5)
project(netlink_example C)

add_executable(show_links show_links.c)
target_link_libraries(show_links ${CONAN_LIBS})
