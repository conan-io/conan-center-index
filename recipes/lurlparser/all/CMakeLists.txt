cmake_minimum_required(VERSION 3.8)
project(LUrlParser LANGUAGES CXX)

add_library(lurlparser ${LURLPARSER_SRC_DIR}/LUrlParser.cpp)
target_include_directories(lurlparser PRIVATE ${LURLPARSER_SRC_DIR})
target_compile_features(lurlparser PRIVATE cxx_std_11)
set_target_properties(lurlparser PROPERTIES
    PUBLIC_HEADER  ${LURLPARSER_SRC_DIR}/LUrlParser.h
    CMAKE_CXX_STANDARD_REQUIRED ON
    CMAKE_CXX_EXTENSIONS OFF
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)

include(GNUInstallDirs)
install(
    TARGETS lurlparser
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
