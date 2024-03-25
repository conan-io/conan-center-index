cmake_minimum_required(VERSION 3.15)
project(fpng LANGUAGES CXX)

include(GNUInstallDirs)

add_library(fpng ${FPNG_SRC_DIR}/src/fpng.cpp)
set_target_properties(fpng PROPERTIES
    PUBLIC_HEADER ${FPNG_SRC_DIR}/src/fpng.h
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)
target_compile_features(fpng PRIVATE cxx_std_11)
if(FPNG_WITH_SSE)
    if (NOT MSVC)
        target_compile_options(fpng PRIVATE -msse4.1 -mpclmul)
    endif()
    target_compile_definitions(fpng PRIVATE -DFPNG_NO_SSE=0)
else()
    target_compile_definitions(fpng PRIVATE -DFPNG_NO_SSE=1)
endif()

find_library(LIBM m)
target_link_libraries(fpng PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)

install(
    TARGETS fpng
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
