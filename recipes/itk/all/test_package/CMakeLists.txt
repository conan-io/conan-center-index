cmake_minimum_required(VERSION 3.7)
project(example)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

include_directories(${CONAN_INCLUDE_DIRS_ITK_SUB})

add_executable(example example.cpp)

target_link_libraries(example ${CONAN_LIBS} )
