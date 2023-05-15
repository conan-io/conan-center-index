cmake_minimum_required(VERSION 3.5)
project(netlink_example C)

find_package(libnl CONFIG REQUIRED)

add_executable(show_links show_links.c)
target_link_libraries(show_links libnl::nl)
