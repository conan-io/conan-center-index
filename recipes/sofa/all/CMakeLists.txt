cmake_minimum_required(VERSION 3.4.3)
project(sofa C)

include(GNUInstallDirs)

if(NOT DEFINED SOFA_SRC_DIR)
    message(FATAL_ERROR "SOFA_SRC_DIR must be set externally")
endif()

file(GLOB SRC_FILES "${SOFA_SRC_DIR}/*.c")
list(REMOVE_ITEM SRC_FILES "${SOFA_SRC_DIR}/t_sofa_c.c")
add_library(sofa_c ${SRC_FILES})

set_target_properties(sofa_c PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)

install(
    TARGETS sofa_c
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(HEADER_FILES ${SOFA_SRC_DIR}/sofa.h ${SOFA_SRC_DIR}/sofam.h)
install(FILES ${HEADER_FILES} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
