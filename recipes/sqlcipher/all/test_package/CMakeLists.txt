cmake_minimum_required(VERSION 3.0)

project(PackageTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example example.c)
if (UNIX)
    target_link_libraries(example ${CONAN_LIBS} m)
else()
    target_link_libraries(example ${CONAN_LIBS})
endif()
