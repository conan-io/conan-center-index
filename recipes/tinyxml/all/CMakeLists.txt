cmake_minimum_required(VERSION 3.4)
project(tinyxml LANGUAGES CXX)

option(TINYXML_WITH_STL "Compile TinyXML with STL" OFF)

set(TINYXML_HDRS
    ${TINYXML_SRC_DIR}/tinystr.h
    ${TINYXML_SRC_DIR}/tinyxml.h)
set(TINYXML_SRCS
    ${TINYXML_SRC_DIR}/tinystr.cpp
    ${TINYXML_SRC_DIR}/tinyxml.cpp
    ${TINYXML_SRC_DIR}/tinyxmlerror.cpp
    ${TINYXML_SRC_DIR}/tinyxmlparser.cpp)

add_library(tinyxml ${TINYXML_SRCS})
target_include_directories(tinyxml PUBLIC ${TINYXML_SRC_DIR})

if(TINYXML_WITH_STL)
    target_compile_definitions(tinyxml PUBLIC TIXML_USE_STL)
endif()

include(GNUInstallDirs)
install(TARGETS tinyxml
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(FILES ${TINYXML_HDRS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
