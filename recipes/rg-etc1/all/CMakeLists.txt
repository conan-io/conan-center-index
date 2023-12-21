cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

if(WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

file(GLOB SRCS_FILES ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp)
file(GLOB HDRS_FILES ${CMAKE_CURRENT_SOURCE_DIR}/src/*.h)

add_library(rg_etc1 ${SRCS_FILES})
target_include_directories(rg_etc1 PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)

include(GNUInstallDirs)
install(TARGETS rg_etc1)
install(FILES ${HDRS_FILES} DESTINATION include)
