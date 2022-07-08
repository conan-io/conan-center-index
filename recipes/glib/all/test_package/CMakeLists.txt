cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

add_executable(${PROJECT_NAME} test_package.c)

find_package(glib CONFIG REQUIRED)
target_link_libraries(${PROJECT_NAME} glib::glib-2.0 glib::gio-2.0 glib::gmodule-2.0 glib::gobject-2.0 glib::gthread-2.0)
