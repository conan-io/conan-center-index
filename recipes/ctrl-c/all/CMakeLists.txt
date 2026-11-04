cmake_minimum_required(VERSION 3.15)
project(ctrl-c LANGUAGES CXX)

add_library(ctrl-c ${CTRL_C_SRC_DIR}/src/ctrl-c.cpp)
set_target_properties(ctrl-c PROPERTIES
    PUBLIC_HEADER ${CTRL_C_SRC_DIR}/src/ctrl-c.h
)
target_compile_features(ctrl-c PUBLIC cxx_std_11)

include(GNUInstallDirs)
install(
    TARGETS ctrl-c
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
