cmake_minimum_required(VERSION 3.8)
project(log.c LANGUAGES C)

option(LOGC_USE_COLOR "Use Color" ON)

add_library(log.c ${LOGC_SRC_FOLDER}/src/log.c)
set_target_properties(log.c PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
target_compile_features(log.c PRIVATE c_std_99)

if(LOGC_USE_COLOR)
    target_compile_definitions(log.c PRIVATE LOG_USE_COLOR)
endif()

include(GNUInstallDirs)
install(FILES ${LOGC_SRC_FOLDER}/src/log.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(
    TARGETS log.c
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
