cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(gobject-introspection REQUIRED CONFIG)

add_executable(test_basic test_basic.c)
target_link_libraries(test_basic PRIVATE gobject-introspection::gobject-introspection)

if(GLIB_INTROSPECTION_DATA_AVAILABLE)
    add_executable(test_girepository test_girepository.c)
    target_link_libraries(test_girepository PRIVATE gobject-introspection::gobject-introspection)
endif()
