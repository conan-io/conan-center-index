cmake_minimum_required(VERSION 3.12)
project(duktape C)

file(GLOB SOURCES ${CMAKE_CURRENT_LIST_DIR}/src/src/*.c)
file(GLOB HEADERS ${CMAKE_CURRENT_LIST_DIR}/src/src/*.h)
add_library(duktape ${SOURCES} ${HEADERS})
set_target_properties(duktape PROPERTIES PUBLIC_HEADER "${HEADERS}")

if (UNIX AND NOT APPLE AND NOT ANDROID)
    target_link_libraries(duktape m)
endif()

include(GNUInstallDirs)
install(
    TARGETS duktape
    PUBLIC_HEADER DESTINATION include
)
