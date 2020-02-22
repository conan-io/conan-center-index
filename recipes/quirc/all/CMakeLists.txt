cmake_minimum_required(VERSION 3.4.3)
project(quirc C)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(QUIRC_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/lib)

add_library(quirc
  ${QUIRC_SOURCE_DIR}/decode.c
  ${QUIRC_SOURCE_DIR}/identify.c
  ${QUIRC_SOURCE_DIR}/quirc.c
  ${QUIRC_SOURCE_DIR}/version_db.c
)

if(WIN32 AND BUILD_SHARED_LIBS)
  set_target_properties(quirc PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
endif()
set_target_properties(quirc PROPERTIES VERSION ${QUIRC_VERSION})

install(
  TARGETS quirc
  EXPORT quirc
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
)

install(FILES ${QUIRC_SOURCE_DIR}/quirc.h DESTINATION include)
