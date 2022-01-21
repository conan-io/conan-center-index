cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(czmq REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_definitions(${PROJECT_NAME} PRIVATE $<$<BOOL:${WITH_LIBSODIUM}>:"WITH_LIBSODIUM">)
if(TARGET czmq-static)
    target_link_libraries(${PROJECT_NAME} czmq-static)
else()
    target_link_libraries(${PROJECT_NAME} czmq)
endif()
