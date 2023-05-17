cmake_minimum_required(VERSION 3.12)
project(qtxlsxwriter LANGUAGES CXX)

find_package(Qt${QT_VERSION_MAJOR} REQUIRED Core Gui CONFIG)

file(GLOB QTXLSXWRITER_SOURCES ${QTXLSXWRITER_SRC_DIR}/src/xlsx/*.cpp)
file(GLOB QTXLSXWRITER_PRIVATE_HEADERS ${QTXLSXWRITER_SRC_DIR}/src/xlsx/*_p.h)
file(GLOB QTXLSXWRITER_PUBLIC_HEADERS ${QTXLSXWRITER_SRC_DIR}/src/xlsx/*.h)
list(REMOVE_ITEM QTXLSXWRITER_PUBLIC_HEADERS ${QTXLSXWRITER_PRIVATE_HEADERS})

add_library(qtxlsxwriter ${QTXLSXWRITER_SOURCES})
target_include_directories(qtxlsxwriter
    PUBLIC
        ${QTXLSXWRITER_SRC_DIR}/src/xlsx>
    PRIVATE
        # qtxlsxwriter uses qt private headers
        ${QT_ROOT}/include/QtCore/${Qt${QT_VERSION_MAJOR}_VERSION}
        ${QT_ROOT}/include/QtGui/${Qt${QT_VERSION_MAJOR}_VERSION}
        ${QT_ROOT}/include/QtGui/${Qt${QT_VERSION_MAJOR}_VERSION}/QtGui
)
target_compile_features(qtxlsxwriter PRIVATE cxx_range_for)
target_link_libraries(qtxlsxwriter PUBLIC Qt${QT_VERSION_MAJOR}::Core Qt${QT_VERSION_MAJOR}::Gui)
set_target_properties(qtxlsxwriter PROPERTIES
    PUBLIC_HEADER "${QTXLSXWRITER_PUBLIC_HEADERS}"
    DEFINE_SYMBOL QT_BUILD_XLSX_LIB
    AUTOMOC ON
)
if(NOT BUILD_SHARED_LIBS)
    target_compile_definitions(qtxlsxwriter PUBLIC QTXLSX_STATIC)
endif()

include(GNUInstallDirs)
install(
    TARGETS qtxlsxwriter
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
