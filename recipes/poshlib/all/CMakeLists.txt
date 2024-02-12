cmake_minimum_required(VERSION 3.12)
project(cmake_wrapper)

if(WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

file(GLOB SRCS_FILES ${CMAKE_CURRENT_SOURCE_DIR}/src/*.c)
file(GLOB HDRS_FILES ${CMAKE_CURRENT_SOURCE_DIR}/src/*.h)

add_library(posh ${SRCS_FILES})
target_include_directories(posh PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)

include(GNUInstallDirs)
install(TARGETS posh)
install(FILES ${HDRS_FILES} DESTINATION include)
