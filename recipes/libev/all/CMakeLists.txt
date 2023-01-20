cmake_minimum_required(VERSION 3.14)
project(ev C)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

set(EV_PUBLIC_HEADERS
    "${EV_SRC_DIR}/ev.h"
    "${EV_SRC_DIR}/config.h")
add_library(ev "${EV_SRC_DIR}/ev.c")
target_link_libraries(ev PUBLIC ws2_32)
target_compile_definitions(ev PRIVATE HAVE_CONFIG_H=1)
target_include_directories(ev PUBLIC ${EV_SRC_DIR})

set_target_properties(ev PROPERTIES PUBLIC_HEADER "${EV_PUBLIC_HEADERS}")
include(GNUInstallDirs)

install(TARGETS ev
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
