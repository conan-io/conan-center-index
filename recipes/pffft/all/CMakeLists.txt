cmake_minimum_required(VERSION 3.4)
project(pffft LANGUAGES C)

include(GNUInstallDirs)

option(DISABLE_SIMD "Use scalar code instead of simd code" OFF)

add_library(pffft ${PFFFT_SRC_DIR}/pffft.c)
if(DISABLE_SIMD)
    target_compile_definitions(pffft PRIVATE PFFFT_SIMD_DISABLE)
endif()
if(MSVC)
    target_compile_definitions(pffft PRIVATE _USE_MATH_DEFINES)
    set_property(TARGET pffft PROPERTY WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
endif()
include(CheckFunctionExists)
check_function_exists(round HAVE_MATH_SYSTEM)
if(NOT HAVE_MATH_SYSTEM)
    target_link_libraries(pffft PRIVATE m)
endif()

install(
  TARGETS pffft
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(FILES ${PFFFT_SRC_DIR}/pffft.h
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
