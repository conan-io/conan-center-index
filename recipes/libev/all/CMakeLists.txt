cmake_minimum_required(VERSION 3.14)
project(ev C)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

set(LIBEV_PUBLIC_HEADERS
    ev.h
    config.h)
add_library(ev ev.c)
target_link_libraries(ev PUBLIC ws2_32)
target_compile_definitions(ev PRIVATE HAVE_CONFIG_H=1)
target_include_directories(ev PUBLIC ${PROJECT_SOURCE_DIR})

set_target_properties(ev PROPERTIES PUBLIC_HEADER "${LIBEV_PUBLIC_HEADERS}")
include(GNUInstallDirs)

install(TARGETS ev
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
