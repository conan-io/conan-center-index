cmake_minimum_required(VERSION 3.15)
project(METIS C)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS TRUE)

include(gkbuild.cmake)

find_package(gklib REQUIRED)

file(GLOB metis_sources libmetis/*.c)
add_library(metis ${metis_sources})
target_include_directories(metis PRIVATE libmetis include)
target_link_libraries(metis PRIVATE gklib::gklib)

include(GNUInstallDirs)
install(TARGETS metis)
install(DIRECTORY include/ DESTINATION include)
