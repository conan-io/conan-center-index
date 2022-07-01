cmake_minimum_required(VERSION 3.4.3)
project(sofa C)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

include(GNUInstallDirs)

set(SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/${SOFA_VERSION}/c/src)
file(GLOB SRC_FILES "${SOURCE_DIR}/*.c")
list(REMOVE_ITEM SRC_FILES "${SOURCE_DIR}/t_sofa_c.c")
add_library(sofa_c ${SRC_FILES})

set_target_properties(sofa_c PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)

install(
    TARGETS sofa_c
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

set(HEADER_FILES ${SOURCE_DIR}/sofa.h ${SOURCE_DIR}/sofam.h)
install(FILES ${HEADER_FILES} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
