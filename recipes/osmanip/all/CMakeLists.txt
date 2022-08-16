cmake_minimum_required(VERSION 3.13)
project(osmanip LANGUAGES CXX)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

find_package(arsenalgear REQUIRED CONFIG)

add_library(osmanip)
target_sources(osmanip PRIVATE
    source_subfolder/src/graphics/canvas.cpp
    source_subfolder/src/graphics/plot_2D.cpp
    $<$<VERSION_EQUAL:${OSMANIP_VERSION},4.0.0>:
        source_subfolder/src/manipulators/csmanip.cpp
    >
    $<$<VERSION_GREATER:${OSMANIP_VERSION},4.0.0>:
        source_subfolder/src/manipulators/printer.cpp
        source_subfolder/src/manipulators/cursor.cpp
        source_subfolder/src/manipulators/common.cpp
        source_subfolder/src/manipulators/colsty.cpp
    >
    source_subfolder/src/progressbar/progress_bar.cpp
    source_subfolder/src/utility/windows.cpp
)
target_include_directories(osmanip PUBLIC source_subfolder/include/)
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
    DIRECTORY source_subfolder/include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/osmanip
)
