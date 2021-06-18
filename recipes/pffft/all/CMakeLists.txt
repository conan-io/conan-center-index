cmake_minimum_required(VERSION 3.4)
project(pffft C)

include(conanbuildinfo.cmake)
conan_basic_setup()

option(DISABLE_SIMD "Use scalar code instead of simd code" OFF)

add_library(${PROJECT_NAME} source_subfolder/pffft.c)
if(DISABLE_SIMD)
  target_compile_definitions(${PROJECT_NAME} PRIVATE PFFFT_SIMD_DISABLE)
endif()
if(MSVC)
  target_compile_definitions(${PROJECT_NAME} PRIVATE _USE_MATH_DEFINES)
  set_property(TARGET ${PROJECT_NAME} PROPERTY WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
endif()
find_library(MATH_LIBRARY m)
if(MATH_LIBRARY)
  target_link_libraries(${PROJECT_NAME} PRIVATE ${MATH_LIBRARY})
endif()

install(
  TARGETS ${PROJECT_NAME}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(FILES source_subfolder/pffft.h
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
