cmake_minimum_required(VERSION 3.4)
project(CQRlib LANGUAGES C)

add_library(CQRlib ${CQRLIB_SRC_DIR}/cqrlib.c)
target_include_directories(CQRlib PRIVATE ${CQRLIB_SRC_DIR})
set_target_properties(CQRlib PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)

find_library(M_LIB m)
if(M_LIB)
    target_link_libraries(CQRlib PRIVATE ${M_LIB})
endif()

include(GNUInstallDirs)
install(TARGETS CQRlib
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES ${CQRLIB_SRC_DIR}/cqrlib.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
