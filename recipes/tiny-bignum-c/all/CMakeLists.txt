cmake_minimum_required(VERSION 3.4)
project(tiny-bignum-c C)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_library(${PROJECT_NAME} source_subfolder/bn.c)
set_target_properties(${PROJECT_NAME} PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)

install(TARGETS ${PROJECT_NAME}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(FILES source_subfolder/bn.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
