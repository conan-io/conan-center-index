cmake_minimum_required(VERSION 3.0.2)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory("source_subfolder")

target_include_directories(squish PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
  $<INSTALL_INTERFACE:include>
)
set_target_properties(squish PROPERTIES CXX_VISIBILITY_PRESET hidden)
include(GenerateExportHeader)
generate_export_header(squish)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/squish_export.h DESTINATION include)
