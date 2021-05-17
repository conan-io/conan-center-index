cmake_minimum_required(VERSION 3.1)
project(MyHello)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

if(NOT APPLE)
    message(FATAL_ERROR "APPLE variable is false")
endif()

add_executable(hello hello.c)
set_target_properties(hello PROPERTIES MACOSX_BUNDLE FALSE)
include_directories(${CONAN_INCLUDE_DIRS})
target_link_libraries(hello ${CONAN_LIBS})
