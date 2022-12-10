cmake_minimum_required(VERSION 3.1)
project(jsmn LANGUAGES C)

add_library(jsmn ${JSMN_SRC_DIR}/jsmn.c)
set_target_properties(jsmn PROPERTIES
    C_VISIBILITY_PRESET hidden
    PUBLIC_HEADER ${JSMN_SRC_DIR}/jsmn.h
)
if(JSMN_PARENT_LINKS)
    target_compile_definitions(jsmn PUBLIC JSMN_PARENT_LINKS)
endif()

include(GNUInstallDirs)
install(
    TARGETS jsmn
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
