cmake_minimum_required(VERSION 3.1)
project(osmanip LANGUAGES CXX)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

include(GNUInstallDirs)

set(osmanip_src
    source_subfolder/src/graphics/canvas.cpp
    source_subfolder/src/graphics/plot_2D.cpp
    source_subfolder/src/manipulators/csmanip.cpp
    source_subfolder/src/progressbar/progress_bar.cpp
    source_subfolder/src/utility/windows.cpp
)

set(osmanip_inc
    source_subfolder/include/graphics/canvas.hpp
    source_subfolder/include/graphics/plot_2D.hpp
    source_subfolder/include/manipulators/csmanip.hpp
    source_subfolder/include/progressbar/multi_progress_bar.hpp
    source_subfolder/include/progressbar/progress_bar.hpp
    source_subfolder/include/utility/windows.hpp
)


add_library(osmanip ${osmanip_src})
target_include_directories(osmanip PUBLIC source_subfolder/include/)
target_compile_features(osmanip PUBLIC cxx_std_17)
set_target_properties(osmanip PROPERTIES
    PUBLIC_HEADER "${osmanip_inc}"
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)

find_library(LIBM m)
target_link_libraries(osmanip PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)

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
