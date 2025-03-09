cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(Intl REQUIRED CONFIG)
find_package(Gettext REQUIRED)

if (NOT GETTEXT_MSGFMT_EXECUTABLE)
    message(FATAL_ERROR "Gettext msgfmt not found.")
endif()

if (NOT GETTEXT_MSGMERGE_EXECUTABLE)
    message(FATAL_ERROR "Gettext msgmerge not found.")
endif()

message(STATUS "Conan gettext msgfmt: ${GETTEXT_MSGFMT_EXECUTABLE}")
message(STATUS "Conan gettext msgmerge: ${GETTEXT_MSGMERGE_EXECUTABLE}")

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Intl::Intl)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
