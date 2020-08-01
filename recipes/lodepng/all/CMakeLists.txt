cmake_minimum_required(VERSION 3.0)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_library(lodepng "source_subfolder/lodepng.h" "source_subfolder/lodepng.cpp")

include(GNUInstallDirs)
install(TARGETS lodepng)
install(FILES "source_subfolder/lodepng.h" DESTINATION include)
