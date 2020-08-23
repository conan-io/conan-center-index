cmake_minimum_required(VERSION 3.1)
project(cspice C)

include(conanbuildinfo.cmake)
conan_basic_setup()

file(GLOB SRC_FILES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/cspice/*.c)
add_library(cspice ${SRC_FILES})

if(WIN32)
  target_compile_definitions(cspice PRIVATE "_COMPLEX_DEFINED;MSDOS;OMIT_BLANK_CC;NON_ANSI_STDIO")
  set_target_properties(cspice PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
elseif(UNIX)
  target_compile_definitions(cspice PRIVATE "NON_UNIX_STDIO")
  target_compile_options(cspice PRIVATE -ansi)
endif()

install(
  TARGETS cspice
  EXPORT cspice
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
)

file(GLOB INCLUDE_FILES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/include/*.h)
install(FILES ${INCLUDE_FILES} DESTINATION include)
