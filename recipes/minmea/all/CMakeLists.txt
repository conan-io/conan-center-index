cmake_minimum_required(VERSION 3.4)
project(wrapper LANGUAGES C)

add_subdirectory(${MINMEA_SRC_DIR})

include(GNUInstallDirs)

install(TARGETS minmea
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}")
install(FILES ${MINMEA_SRC_DIR}/minmea.h 
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
if(MSVC)
    install(FILES ${MINMEA_SRC_DIR}/compat/minmea_compat_windows.h
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
        RENAME minmea_compat.h)
endif()
