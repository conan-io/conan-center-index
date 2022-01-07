cmake_minimum_required(VERSION 3.1)

project(wineditline_wrapper C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

set(src source_subfolder/src)

add_library(edit "${src}/editline.c" "${src}/fn_complete.c" "${src}/history.c")
if(BUILD_SHARED_LIBS)
  target_sources(edit PRIVATE "${src}/libedit.def")
endif()

target_include_directories(edit PRIVATE "${src}")

include(GNUInstallDirs)

install(
    TARGETS edit
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
)

install(DIRECTORY "${src}/editline" DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")
