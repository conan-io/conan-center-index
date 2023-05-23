cmake_minimum_required(VERSION 3.4)
project(tiny-bignum-c LANGUAGES C)

add_library(tiny-bignum-c ${TINY_BIGNUM_C_SRC_DIR}/bn.c)
set_target_properties(tiny-bignum-c PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)

include(GNUInstallDirs)
install(TARGETS tiny-bignum-c
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(FILES ${TINY_BIGNUM_C_SRC_DIR}/bn.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
