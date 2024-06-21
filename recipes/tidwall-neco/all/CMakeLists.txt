cmake_minimum_required(VERSION 3.15)
project(neco LANGUAGES C)

include(GNUInstallDirs)

add_library(neco ${TIDWALL_NECO_SRC_DIR}/neco.c)
target_include_directories(neco PRIVATE ${TIDWALL_NECO_SRC_DIR})
set_target_properties(neco PROPERTIES
    PUBLIC_HEADER ${TIDWALL_NECO_SRC_DIR}/neco.h
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)
target_compile_features(neco PRIVATE c_std_11)

install(
    TARGETS neco
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
