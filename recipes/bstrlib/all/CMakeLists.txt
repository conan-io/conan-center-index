cmake_minimum_required(VERSION 3.4)
project(bstrlib C)

# Headers Variable
set (bstrlib_HEADERS
        "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/bstrlib.h"
        "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/bstraux.h"
        "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/bsafe.h"
        "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/buniutil.h"
        "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/utf8util.h")

# Sources Variable
set (bstrlib_CPP
        "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/bstrlib.c"
        "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/bstraux.c"
        "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/bsafe.c"
        "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/buniutil.c"
        "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/utf8util.c")

add_library(${PROJECT_NAME} ${bstrlib_HEADERS} ${bstrlib_CPP})

install(
  TARGETS ${PROJECT_NAME}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(FILES ${bstrilib_HEADERS}
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
