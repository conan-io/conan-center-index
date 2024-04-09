cmake_minimum_required(VERSION 3.12)
project(cmake_wrapper LANGUAGES CXX)

find_package(libfuse REQUIRED CONFIG)

set(SOURCE_SUBFOLDER ${CMAKE_CURRENT_LIST_DIR}/src)

file(GLOB_RECURSE INCLUDE_FILES "${SOURCE_SUBFOLDER}/Fuse*.h" "${SOURCE_SUBFOLDER}/Fuse.cpp")

add_library(fusepp ${SOURCE_SUBFOLDER}/Fuse.cpp)
target_link_libraries(fusepp PUBLIC libfuse::libfuse)
set_target_properties(fusepp PROPERTIES PUBLIC_HEADER "${INCLUDE_FILES}")

include(GNUInstallDirs)
install(TARGETS fusepp
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
