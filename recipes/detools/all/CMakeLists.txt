cmake_minimum_required(VERSION 3.12)
project(detools C)

find_package(heatshrink REQUIRED)
find_package(lz4 REQUIRED)
find_package(LibLZMA REQUIRED)

add_library(detools src/c/detools.c)
target_link_libraries(detools
    heatshrink::heatshrink
    lz4::lz4
    LibLZMA::LibLZMA
)

include(GNUInstallDirs)
install(TARGETS detools)
install(FILES src/c/detools.h DESTINATION include)
