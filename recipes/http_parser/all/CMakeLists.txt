cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper LANGUAGES C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

add_library(http_parser
    source_subfolder/http_parser.c)

install(TARGETS http_parser
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin)

install(FILES source_subfolder/http_parser.h
    DESTINATION include)
