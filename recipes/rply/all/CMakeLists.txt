cmake_minimum_required(VERSION 3.4)
project(rply LANGUAGES C)

add_library(rply ${RPLY_SRC_DIR}/rply.c)
target_include_directories(rply PUBLIC ${RPLY_SRC_DIR})
set_target_properties(rply PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

include(GNUInstallDirs)
install(
    TARGETS rply
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
install(
    FILES ${RPLY_SRC_DIR}/rply.h ${RPLY_SRC_DIR}/rplyfile.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
