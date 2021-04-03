cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example example.cpp)

if(NOT BUILD_SHARED_LIBS)
    target_compile_definitions(example PRIVATE RMLUI_STATIC_LIB)
endif()

target_link_libraries(example ${CONAN_LIBS})
