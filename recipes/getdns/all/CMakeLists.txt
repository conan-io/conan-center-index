cmake_minimum_required(VERSION 3.12)
project(cmake_wrapper)

find_package(libidn2 REQUIRED)

link_libraries(
    libidn2::libidn2
)

add_subdirectory(src)
