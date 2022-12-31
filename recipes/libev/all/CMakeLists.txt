cmake_minimum_required(VERSION 3.14)
project(ev C)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

set(LIBEV_PUBLIC_HEADERS
    ev.h
    config.h)
add_library(ev ev.c ${LIBEV_PUBLIC_HEADERS})
target_link_libraries(ev PUBLIC ws2_32)
target_compile_definitions(ev PRIVATE HAVE_CONFIG_H=1)
target_include_directories(ev PUBLIC ${PROJECT_SOURCE_DIR})

set_target_properties(ev PROPERTIES PUBLIC_HEADER "${LIBEV_PUBLIC_HEADERS}")
include(GNUInstallDirs)

install(TARGETS ev
    EXPORT ${EXPORT_NAME}Targets DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} COMPONENT runtime
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR} COMPONENT devel
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR} COMPONENT devel
)
