cmake_minimum_required(VERSION 3.4.3)
project(quirc LANGUAGES C)

include(GNUInstallDirs)

set(QUIRC_MAX_REGIONS 254 CACHE STRING "Maximum number of regions")

add_library(quirc
    ${QUIRC_SRC_DIR}/decode.c
    ${QUIRC_SRC_DIR}/identify.c
    ${QUIRC_SRC_DIR}/quirc.c
    ${QUIRC_SRC_DIR}/version_db.c
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

install(FILES ${QUIRC_SRC_DIR}/quirc.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
