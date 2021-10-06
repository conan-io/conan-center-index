cmake_minimum_required(VERSION 3.1)
project(perfetto CXX)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(Threads)

set(PUBLIC_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/sdk/perfetto.h)

add_library(perfetto source_subfolder/sdk/perfetto.cc)
set_target_properties(perfetto PROPERTIES PUBLIC_HEADER "${PUBLIC_HEADERS}")

install(
  TARGETS perfetto
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

if (WIN32)
  # The perfetto library contains many symbols, so it needs the big object
  # format.
  target_compile_options(perfetto PRIVATE "/bigobj")
  # Disable legacy features in windows.h.
  add_definitions(-DWIN32_LEAN_AND_MEAN -DNOMINMAX)
  # On Windows we should link to WinSock2.
  target_link_libraries(perfetto ws2_32)
endif (WIN32)

if (MSVC)
  target_compile_options(perfetto PRIVATE "/permissive-")
endif (MSVC)
