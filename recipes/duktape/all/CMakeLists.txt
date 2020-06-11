cmake_minimum_required(VERSION 3.1)

project(duktape C)

include(conanbuildinfo.cmake)
conan_basic_setup()

file(GLOB SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/*.c)
file(GLOB HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/*.h)
message(STATUS "SOURCES= ${SOURCES} HEADERS=${HEADERS}")
add_library(duktape ${SOURCES} ${HEADERS})
set_target_properties(duktape PROPERTIES PUBLIC_HEADER "${HEADERS}")

if (NOT WIN32)
    target_link_libraries(duktape m)
endif()

install(
    TARGETS duktape
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    PUBLIC_HEADER DESTINATION include
)
