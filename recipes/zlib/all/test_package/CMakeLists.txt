cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(ZLIB REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE ZLIB::ZLIB)

# When the zlib package is built with enable_zlibwapi=True, exercise the
# WINAPI/stdcall variant through its dedicated component. Note that the
# ZLIB::ZLIB target above must keep working in that configuration too.
if(ZLIB_WITH_ZLIBWAPI)
    add_executable(${PROJECT_NAME}_wapi test_package_wapi.c)
    target_link_libraries(${PROJECT_NAME}_wapi PRIVATE ZLIB::zlibwapi)
endif()
