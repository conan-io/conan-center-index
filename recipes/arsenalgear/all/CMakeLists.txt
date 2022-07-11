cmake_minimum_required(VERSION 3.8)
project(arsenalgear LANGUAGES CXX)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

include(GNUInstallDirs)

set(arsenalgear_src
    source_subfolder/src/operators.cpp
    source_subfolder/src/stream.cpp
    source_subfolder/src/system.cpp
    source_subfolder/src/utils.cpp
)

set(arsenalgear_inc
    source_subfolder/include/constants.hpp
    source_subfolder/include/math.hpp
    source_subfolder/include/operators.hpp
    source_subfolder/include/stream.hpp
    source_subfolder/include/system.hpp
    source_subfolder/include/utils.hpp
)

add_library(arsenalgear ${arsenalgear_src})
target_include_directories(arsenalgear PRIVATE "source_subfolder/include")
set_target_properties(arsenalgear PROPERTIES
    PUBLIC_HEADER "${arsenalgear_inc}"
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)
target_compile_features(arsenalgear PUBLIC cxx_std_17)

find_library(LIBM m)
target_link_libraries(arsenalgear PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)

install(
    TARGETS arsenalgear
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/arsenalgear
)
