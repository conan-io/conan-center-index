cmake_minimum_required(VERSION 3.13)
project(osmanip LANGUAGES CXX)

find_package(arsenalgear REQUIRED CONFIG)

add_library(osmanip)
target_sources(osmanip PRIVATE
    ${OSMANIP_SRC_DIR}/src/graphics/canvas.cpp
    ${OSMANIP_SRC_DIR}/src/graphics/plot_2D.cpp
    $<$<VERSION_GREATER_EQUAL:${OSMANIP_VERSION},4.2.0>:
        ${OSMANIP_SRC_DIR}/src/manipulators/colsty.cpp
        ${OSMANIP_SRC_DIR}/src/manipulators/common.cpp
        ${OSMANIP_SRC_DIR}/src/manipulators/cursor.cpp
        ${OSMANIP_SRC_DIR}/src/manipulators/decorator.cpp
    >
    $<$<AND:$<VERSION_GREATER_EQUAL:${OSMANIP_VERSION},4.1.0>,$<VERSION_LESS:${OSMANIP_VERSION},4.2.0>>:
        ${OSMANIP_SRC_DIR}/src/manipulators/colsty.cpp
        ${OSMANIP_SRC_DIR}/src/manipulators/common.cpp
        ${OSMANIP_SRC_DIR}/src/manipulators/cursor.cpp
        ${OSMANIP_SRC_DIR}/src/manipulators/printer.cpp
    >
    $<$<VERSION_EQUAL:${OSMANIP_VERSION},4.0.0>:
        ${OSMANIP_SRC_DIR}/src/manipulators/csmanip.cpp
    >
    $<$<VERSION_LESS:${OSMANIP_VERSION},4.2.0>:
        ${OSMANIP_SRC_DIR}/src/progressbar/progress_bar.cpp
    >
    ${OSMANIP_SRC_DIR}/src/utility/windows.cpp
)
target_include_directories(osmanip PUBLIC ${OSMANIP_SRC_DIR}/include/)
target_compile_features(osmanip PUBLIC cxx_std_17)
set_target_properties(osmanip PROPERTIES
    PUBLIC_HEADER "${osmanip_inc}"
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)

target_link_libraries(osmanip PRIVATE arsenalgear::arsenalgear)

find_library(LIBM m)
target_link_libraries(osmanip PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)

include(GNUInstallDirs)

install(
    TARGETS osmanip
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(
    DIRECTORY ${OSMANIP_SRC_DIR}/include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/osmanip
)
