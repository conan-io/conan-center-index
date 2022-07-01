cmake_minimum_required(VERSION 3.4.3)
project(quirc C)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

include(GNUInstallDirs)

set(QUIRC_MAX_REGIONS 254 CACHE STRING "Maximum number of regions")

set(QUIRC_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/lib)

add_library(quirc
  ${QUIRC_SOURCE_DIR}/decode.c
  ${QUIRC_SOURCE_DIR}/identify.c
  ${QUIRC_SOURCE_DIR}/quirc.c
  ${QUIRC_SOURCE_DIR}/version_db.c
)

target_compile_definitions(quirc PRIVATE QUIRC_MAX_REGIONS=${QUIRC_MAX_REGIONS})
set_target_properties(quirc PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS TRUE
    VERSION ${QUIRC_VERSION}
)

install(
  TARGETS quirc
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(FILES ${QUIRC_SOURCE_DIR}/quirc.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
