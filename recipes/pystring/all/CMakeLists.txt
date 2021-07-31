cmake_minimum_required(VERSION 3.4)
project(pystring)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_library(${PROJECT_NAME} source_subfolder/pystring.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY WINDOWS_EXPORT_ALL_SYMBOLS TRUE)

install(TARGETS ${PROJECT_NAME}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(FILES source_subfolder/pystring.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
