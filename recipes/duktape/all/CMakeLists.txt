cmake_minimum_required(VERSION 2.8.12)

project(duktape C)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

file(GLOB SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/*.c)
file(GLOB HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/*.h)
add_library(duktape ${SOURCES} ${HEADERS})
set_target_properties(duktape PROPERTIES PUBLIC_HEADER "${HEADERS}")

if (UNIX AND NOT APPLE AND NOT ANDROID)
    target_link_libraries(duktape m)
endif()

install(
    TARGETS duktape
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    PUBLIC_HEADER DESTINATION include
)
