cmake_minimum_required(VERSION 3.4.3)
project(whereami C)

include(conanbuildinfo.cmake)
conan_basic_setup()

if (WIN32 AND BUILD_SHARED_LIBS)
  set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

set(WHEREAMI_SRC "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder")

set(SOURCE_FILES ${WHEREAMI_SRC}/src/whereami.c)
set(HEADER_FILES ${WHEREAMI_SRC}/src/whereami.h)

add_library(${CMAKE_PROJECT_NAME} ${SOURCE_FILES} ${HEADER_FILES})
target_include_directories(${CMAKE_PROJECT_NAME} PUBLIC ${WHEREAMI_SRC}/src)
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY C_STANDARD 99)

install(TARGETS ${CMAKE_PROJECT_NAME}
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

install(FILES ${HEADER_FILES} DESTINATION include)
