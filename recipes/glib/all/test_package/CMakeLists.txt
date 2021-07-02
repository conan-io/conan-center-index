cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
find_package(glib REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} glib::glib-2.0 glib::gio-2.0 glib::gmodule-2.0 glib::gobject-2.0 glib::gthread-2.0)
