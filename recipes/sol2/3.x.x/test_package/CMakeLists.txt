cmake_minimum_required(VERSION 2.8.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp sol_test.hpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
TARGET_COMPILE_DEFINITIONS (${PROJECT_NAME} PUBLIC -DCOMPILE_AS_CPP )
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

enable_testing()

add_test(NAME ${PROJECT_NAME} COMMAND ${PROJECT_NAME})
