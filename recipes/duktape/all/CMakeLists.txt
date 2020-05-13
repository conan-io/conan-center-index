cmake_minimum_required(VERSION 2.8.11)
cmake_minimum_required(VERSION 3.1)

project(duktape C)

include(conanbuildinfo.cmake)
conan_basic_setup()

file(GLOB SRC_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/*.c
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/*.h)
add_library(duktape ${SRC_FILES})

install(
  TARGETS duktape
  EXPORT duktape
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
)

file(GLOB INCLUDE_FILES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/include/*.h)
install(FILES ${INCLUDE_FILES} DESTINATION include)
