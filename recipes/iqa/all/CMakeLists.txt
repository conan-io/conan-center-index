cmake_minimum_required(VERSION 3.12)
project(cmake_wrapper)

if(MSVC AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

file(GLOB IQA_SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/src/source/*.c)
file(GLOB IQA_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/src/include/*.h)

add_library(iqa ${IQA_SOURCES})
target_include_directories(iqa PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src/include)

include(GNUInstallDirs)
install(TARGETS iqa)
install(FILES ${IQA_HEADERS} DESTINATION include)
