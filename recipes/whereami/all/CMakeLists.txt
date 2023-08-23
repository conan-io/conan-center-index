cmake_minimum_required(VERSION 3.12)
project(whereami C)

if (WIN32 AND BUILD_SHARED_LIBS)
  set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

set(WHEREAMI_SRC "${CMAKE_CURRENT_SOURCE_DIR}/src")

set(SOURCE_FILES ${WHEREAMI_SRC}/src/whereami.c)
set(HEADER_FILES ${WHEREAMI_SRC}/src/whereami.h)

add_library(${CMAKE_PROJECT_NAME} ${SOURCE_FILES} ${HEADER_FILES})
target_include_directories(${CMAKE_PROJECT_NAME} PUBLIC ${WHEREAMI_SRC}/src)
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY C_STANDARD 99)

include(GNUInstallDirs)
install(TARGETS ${CMAKE_PROJECT_NAME})
install(FILES ${HEADER_FILES} DESTINATION include)
