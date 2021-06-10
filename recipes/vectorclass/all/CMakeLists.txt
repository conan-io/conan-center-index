cmake_minimum_required(VERSION 3.0)

project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/instrset_detect.cpp)

file(GLOB HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/*.h")

add_library(vectorclass STATIC ${SOURCES} ${HEADERS})

set_target_properties(vectorclass PROPERTIES PUBLIC_HEADER "${HEADERS}")

include(GNUInstallDirs)
install(TARGETS vectorclass
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
