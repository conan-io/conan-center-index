cmake_minimum_required(VERSION 3.4)
project(IrrXML CXX)

include("conanbuildinfo.cmake")
conan_basic_setup()

set(SOURCES
    ${CMAKE_SOURCE_DIR}/source_subfolder/src/CXMLReaderImpl.h
    ${CMAKE_SOURCE_DIR}/source_subfolder/src/fast_atof.h
    ${CMAKE_SOURCE_DIR}/source_subfolder/src/heapsort.h
    ${CMAKE_SOURCE_DIR}/source_subfolder/src/irrArray.h
    ${CMAKE_SOURCE_DIR}/source_subfolder/src/irrString.h
    ${CMAKE_SOURCE_DIR}/source_subfolder/src/irrTypes.h
    ${CMAKE_SOURCE_DIR}/source_subfolder/src/irrXML.cpp
    ${CMAKE_SOURCE_DIR}/source_subfolder/src/irrXML.h
)

add_library(${CMAKE_PROJECT_NAME} ${SOURCES})
if ( MSVC )
  target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE _SCL_SECURE_NO_WARNINGS)
  target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE _CRT_SECURE_NO_WARNINGS)
endif ( MSVC )

if (WIN32 AND BUILD_SHARED_LIBS)
    set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES
                      PUBLIC_HEADER source_subfolder/src/irrXML.h)

install(TARGETS ${CMAKE_PROJECT_NAME}
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
    PUBLIC_HEADER DESTINATION include)
