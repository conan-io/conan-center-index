cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

if(WIN32)
    add_definitions(-D_WIN32_WINNT=0x0601)
endif()

find_package(LibtorrentRasterbar REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE LibtorrentRasterbar::torrent-rasterbar)
if(LibtorrentRasterbar_VERSION VERSION_LESS "2.0")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
endif()
