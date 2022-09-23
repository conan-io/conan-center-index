cmake_minimum_required(VERSION 3.4)
project(http_parser LANGUAGES C)

include(GNUInstallDirs)

add_library(http_parser ${HTTP_PARSER_SRC_DIR}/http_parser.c)
set_target_properties(http_parser PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

install(TARGETS http_parser
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})

install(FILES ${HTTP_PARSER_SRC_DIR}/http_parser.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
