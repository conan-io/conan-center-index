cmake_minimum_required(VERSION 3.15)
project(osmanip LANGUAGES CXX)

find_package(arsenalgear REQUIRED CONFIG)

add_library(osmanip)
target_sources(osmanip PRIVATE
    src/graphics/canvas.cpp
    src/graphics/plot_2D.cpp
    $<$<VERSION_GREATER_EQUAL:${OSMANIP_VERSION},4.4.0>:
        src/utility/iostream.cpp
        src/utility/output_redirector.cpp
        src/utility/sstream.cpp
        src/utility/strings.cpp
    >
    $<$<VERSION_GREATER_EQUAL:${OSMANIP_VERSION},4.2.0>:
        src/manipulators/colsty.cpp
        src/manipulators/common.cpp
        src/manipulators/cursor.cpp
        src/manipulators/decorator.cpp
    >
    $<$<AND:$<VERSION_GREATER_EQUAL:${OSMANIP_VERSION},4.1.0>,$<VERSION_LESS:${OSMANIP_VERSION},4.2.0>>:
        src/manipulators/colsty.cpp
        src/manipulators/common.cpp
        src/manipulators/cursor.cpp
        src/manipulators/printer.cpp
    >
    $<$<VERSION_EQUAL:${OSMANIP_VERSION},4.0.0>:
        src/manipulators/csmanip.cpp
    >
    $<$<VERSION_LESS:${OSMANIP_VERSION},4.2.0>:
        src/progressbar/progress_bar.cpp
    >
    src/utility/windows.cpp
)
target_include_directories(osmanip PUBLIC include/)
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
    DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/osmanip
)
