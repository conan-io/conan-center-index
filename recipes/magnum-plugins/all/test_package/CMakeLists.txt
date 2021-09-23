cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

set(CONAN_CMAKE_SILENT_OUTPUT 1)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(MagnumPlugins REQUIRED)

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/configure.h.in
               ${CMAKE_CURRENT_BINARY_DIR}/configure.h)

add_executable(${PROJECT_NAME} test_package.cpp)
# Intentionally linking with the global 'MagnumPlugins::MagnumPlugins' target, I want to check it is a valid target (although it might be empty)
target_link_libraries(${PROJECT_NAME} Magnum::Trade MagnumPlugins::MagnumPlugins)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        CXX_STANDARD 11
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
)
