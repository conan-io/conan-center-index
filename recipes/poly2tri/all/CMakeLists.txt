cmake_minimum_required(VERSION 3.4)
project(poly2tri)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/poly2tri)

add_library(${PROJECT_NAME}
  ${SRC_DIR}/common/shapes.cc
  ${SRC_DIR}/sweep/advancing_front.cc
  ${SRC_DIR}/sweep/cdt.cc
  ${SRC_DIR}/sweep/sweep.cc
  ${SRC_DIR}/sweep/sweep_context.cc
)

if(MSVC AND BUILD_SHARED_LIBS)
  set_property(TARGET ${PROJECT_NAME} PROPERTY WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

install(
  TARGETS ${PROJECT_NAME}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(
  DIRECTORY ${SRC_DIR}
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  FILES_MATCHING PATTERN "*.h"
)
