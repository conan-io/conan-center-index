cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper)

add_subdirectory(${IDNA_SRC_DIR})

include(GNUInstallDirs)

install(
    TARGETS ada-idna
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(
    FILES 
    ${IDNA_SRC_DIR}/include/idna.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(
    DIRECTORY
    ${IDNA_SRC_DIR}/include/ada
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
