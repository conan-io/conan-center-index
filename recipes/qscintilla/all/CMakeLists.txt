# Reproduces https://github.com/brCreate/QScintilla/blob/6cdb1f9876038ad3ce5955ee473b8f8e503aa2d5/src/qscintilla.pro
cmake_minimum_required(VERSION 3.15)
project(QScintilla LANGUAGES CXX)

option(QSCINTILLA_BUILD_DESIGNER_PLUGIN "Build the QScintilla designer plugin" OFF)

if(NOT DEFINED CMAKE_POSITION_INDEPENDENT_CODE)
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)
endif()
if(NOT DEFINED CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 11)
endif()
set(CMAKE_AUTOMOC ON)

find_package(Qt6 REQUIRED)
if(NOT Qt6_FOUND)
    find_package(Qt5 REQUIRED)
endif()

set(LIB_NAME "qscintilla2_qt${QT_VERSION_MAJOR}")
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    if(APPLE)
        string(APPEND LIB_NAME "_debug")
    elseif(WIN32)
        string(APPEND LIB_NAME "d")
    endif()
endif()
if(NOT BUILD_SHARED_LIBS)
    string(APPEND LIB_NAME "_static")
endif()

file(GLOB SOURCES
    scintilla/src/*.cpp
    scintilla/lexlib/*.cpp
    scintilla/lexers/*.cpp
    src/*.cpp
)
file(GLOB HEADERS
    scintilla/src/*.h
    scintilla/lexlib/*.h
    scintilla/include/*.h
    src/*.h
    src/Qsci/*.h
)
if(IOS)
    list(REMOVE_ITEM SOURCES src/qsciprinter.cpp)
    list(REMOVE_ITEM HEADERS src/Qsci/qsciprinter.h)
endif()

add_library(QScintilla ${SOURCES} ${HEADERS})
set_target_properties(QScintilla PROPERTIES OUTPUT_NAME ${LIB_NAME})
target_include_directories(QScintilla
    PUBLIC
        src
    PRIVATE
        scintilla/include
        scintilla/lexlib
        scintilla/src
)
target_compile_definitions(QScintilla PRIVATE
    SCINTILLA_QT
    SCI_LEXER
    INCLUDE_DEPRECATED_FEATURES
)
if(BUILD_SHARED_LIBS)
    target_compile_definitions(QScintilla PRIVATE QSCINTILLA_MAKE_DLL)
endif()

target_link_libraries(QScintilla PUBLIC Qt${QT_VERSION_MAJOR}::Widgets)
if(NOT IOS)
    target_link_libraries(QScintilla PUBLIC Qt${QT_VERSION_MAJOR}::PrintSupport)
endif()
if(QT_VERSION_MAJOR EQUAL 5 AND APPLE)
    target_link_libraries(QScintilla PUBLIC Qt5::MacExtras)
endif()

if(QSCINTILLA_BUILD_DESIGNER_PLUGIN)
    # Reproduces https://github.com/brCreate/QScintilla/blob/6cdb1f9876038ad3ce5955ee473b8f8e503aa2d5/designer/designer.pro
    add_library(qscintillaplugin MODULE designer/qscintillaplugin.cpp)
    target_link_libraries(qscintillaplugin PRIVATE
        QScintilla
        Qt${QT_VERSION_MAJOR}::Widgets
        Qt${QT_VERSION_MAJOR}::Designer
    )
    include(GNUInstallDirs)
    install(TARGETS qscintillaplugin DESTINATION ${CMAKE_INSTALL_LIBDIR}/qt/plugins/designer)
endif()

include(GNUInstallDirs)
install(TARGETS QScintilla
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
install(DIRECTORY src/Qsci DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
file(GLOB TRANSLATION_FILES src/qscintilla_*.qm)
install(FILES ${TRANSLATION_FILES} DESTINATION ${CMAKE_INSTALL_DATADIR}/translations)
if(BUILD_SHARED_LIBS)
    install(FILES src/features/qscintilla2.prf DESTINATION ${CMAKE_INSTALL_DATADIR}/mkspecs/features)
else()
    install(FILES src/features_staticlib/qscintilla2.prf DESTINATION ${CMAKE_INSTALL_DATADIR}/mkspecs/features)
endif()
