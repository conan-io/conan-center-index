cmake_minimum_required(VERSION 3.15)
project(hdf5-blosc2 C)

include(GNUInstallDirs)

find_package(HDF5 REQUIRED CONFIG)
find_package(c-blosc2 REQUIRED CONFIG)

set(SRC "${HDF5_BLOSC2_SRC_DIR}/src")

add_library(blosc2_filter "${SRC}/blosc2_filter.c")
target_include_directories(blosc2_filter PUBLIC
    $<BUILD_INTERFACE:${SRC}>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)

target_link_libraries(blosc2_filter
    PUBLIC  c-blosc2::c-blosc2
    PRIVATE HDF5::HDF5)

install(TARGETS blosc2_filter
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(FILES "${SRC}/blosc2_filter.h" DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})