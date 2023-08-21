cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

enable_testing()

find_package(libverto REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE libverto::libverto)

if(LIBVERTO_WITH_GLIB)
    add_test(NAME libverto_with_glib COMMAND ${PROJECT_NAME} glib)
endif()
if(LIBVERTO_WITH_LIBEV)
    add_test(NAME libverto_with_libev COMMAND ${PROJECT_NAME} libev)
endif()
if(LIBVERTO_WITH_LIBEVENT)
    add_test(NAME libverto_with_libevent COMMAND ${PROJECT_NAME} libevent)
endif()
if(LIBVERTO_WITH_TEVENT)
    add_test(NAME libverto_with_tevent COMMAND ${PROJECT_NAME} tevent)
endif()
