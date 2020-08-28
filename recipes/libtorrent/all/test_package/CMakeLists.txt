cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if(WIN32)
    add_definitions(-D_WIN32_WINNT=0x0601)
endif()

find_package(LibtorrentRasterbar REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} LibtorrentRasterbar::torrent-rasterbar)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
