cmake_minimum_required(VERSION 3.8)
project(perfetto LANGUAGES CXX)

set(PUBLIC_HEADERS ${PERFETTO_SRC_DIR}/sdk/perfetto.h)

add_library(perfetto ${PERFETTO_SRC_DIR}/sdk/perfetto.cc)
target_compile_features(perfetto PRIVATE ${PERFETTO_CXX_STANDARD})
set_target_properties(perfetto PROPERTIES
    PUBLIC_HEADER "${PUBLIC_HEADERS}"
    WINDOWS_EXPORT_ALL_SYMBOLS TRUE
)

if(PERFETTO_DISABLE_LOGGING)
    target_compile_definitions(perfetto PUBLIC PERFETTO_DISABLE_LOG)
endif()

if (WIN32)
  # Disable legacy features in windows.h.
  target_compile_definitions(perfetto PRIVATE WIN32_LEAN_AND_MEAN NOMINMAX)
  # On Windows we should link to WinSock2.
  target_link_libraries(perfetto PRIVATE ws2_32)
endif (WIN32)

if (MSVC)
  # The perfetto library contains many symbols, so it needs the big object
  # format.
  target_compile_options(perfetto PRIVATE "/bigobj")
  # The perfetto library needs permissive flag on MSVC
  target_compile_options(perfetto PRIVATE "/permissive-")
  # https://devblogs.microsoft.com/cppblog/msvc-now-correctly-reports-__cplusplus/
  target_compile_options(perfetto PRIVATE "/Zc:__cplusplus")
endif (MSVC)

include(GNUInstallDirs)
install(
  TARGETS perfetto
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
