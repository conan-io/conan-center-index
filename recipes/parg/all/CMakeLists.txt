cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper)

add_subdirectory(src)
set_target_properties(parg PROPERTIES PUBLIC_HEADER "${CMAKE_CURRENT_SOURCE_DIR}/src/parg.h")
install(TARGETS parg)
