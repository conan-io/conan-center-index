cmake_minimum_required(VERSION 3.15)
project(mmeter LANGUAGES CXX)

add_library(mmeter ${MMETER_SRC_DIR}/src/MMeter.cpp)
target_include_directories(mmeter PUBLIC ${MMETER_SRC_DIR}/include)
set_target_properties(mmeter PROPERTIES
PUBLIC_HEADER ${MMETER_SRC_DIR}/include/MMeter.h
    WINDOWS_EXPORT_ALL_SYMBOLS ON
    CXX_EXTENSIONS OFF
)

include(GNUInstallDirs)
install(
    TARGETS mmeter
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
