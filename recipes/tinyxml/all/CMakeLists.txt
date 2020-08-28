cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

option(TINYXML_WITH_STL "Compile TinyXML with STL" OFF)

set(SOURCE_SUBFOLDER "source_subfolder")

if(MSVC AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

set(TINYXML_HDRS
    ${CMAKE_CURRENT_SOURCE_DIR}/${SOURCE_SUBFOLDER}/tinystr.h
    ${CMAKE_CURRENT_SOURCE_DIR}/${SOURCE_SUBFOLDER}/tinyxml.h)
set(TINYXML_SRCS
    ${CMAKE_CURRENT_SOURCE_DIR}/${SOURCE_SUBFOLDER}/tinystr.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/${SOURCE_SUBFOLDER}/tinyxml.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/${SOURCE_SUBFOLDER}/tinyxmlerror.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/${SOURCE_SUBFOLDER}/tinyxmlparser.cpp)

add_library(tinyxml STATIC ${TINYXML_SRCS})
target_include_directories(tinyxml PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/${SOURCE_SUBFOLDER})

if(TINYXML_WITH_STL)
    target_compile_definitions(tinyxml PUBLIC TIXML_USE_STL)
endif()

install(TARGETS tinyxml
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib)
install(FILES ${TINYXML_HDRS} DESTINATION include)
