cmake_minimum_required(VERSION 3.4)
project(pffft C)

include(conanbuildinfo.cmake)
conan_basic_setup()

option(DISABLE_SIMD "Use scalar code instead of simd code" OFF)

add_library(${PROJECT_NAME} STATIC source_subfolder/pffft.c
                                   source_subfolder/pffft.h)
if(DISABLE_SIMD)
  target_compile_definitions(${PROJECT_NAME} PRIVATE PFFFT_SIMD_DISABLE)
endif()
if(MSVC)
  target_compile_definitions(${PROJECT_NAME} PRIVATE _USE_MATH_DEFINES)
else()
  target_link_libraries(${PROJECT_NAME} PRIVATE m)
endif()

install(
  TARGETS ${PROJECT_NAME}
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib)

install(
  DIRECTORY source_subfolder/
  DESTINATION include
  FILES_MATCHING
  PATTERN "pffft.h")
