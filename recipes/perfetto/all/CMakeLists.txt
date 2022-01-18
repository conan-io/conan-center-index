cmake_minimum_required(VERSION 3.8)
project(perfetto CXX)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(PUBLIC_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/sdk/perfetto.h)

add_library(perfetto source_subfolder/sdk/perfetto.cc)
target_compile_features(perfetto PRIVATE cxx_std_11 cxx_constexpr)
set_target_properties(perfetto PROPERTIES PUBLIC_HEADER "${PUBLIC_HEADERS}")

install(
  TARGETS perfetto
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

if (PERFETTO_DISABLE_LOGGING)
    add_definitions(-DPERFETTO_DISABLE_LOG)
endif (PERFETTO_DISABLE_LOGGING)

if (WIN32)
  # Disable legacy features in windows.h.
  add_definitions(-DWIN32_LEAN_AND_MEAN -DNOMINMAX)
  # On Windows we should link to WinSock2.
  target_link_libraries(perfetto ws2_32)
endif (WIN32)

if (MSVC)
  # The perfetto library contains many symbols, so it needs the big object
  # format.
  target_compile_options(perfetto PRIVATE "/bigobj")
  # The perfetto library needs permissive flag on MSVC
  target_compile_options(perfetto PRIVATE "/permissive-")
  # The perfetto library doesn't export symbols by default
  set_target_properties(perfetto PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
endif (MSVC)
