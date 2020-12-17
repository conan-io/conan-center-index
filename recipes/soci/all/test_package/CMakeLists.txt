cmake_minimum_required(VERSION 3.1)

project(conanSociTests CXX)

if(    CMAKE_CXX_COMPILER_ID STREQUAL "GNU"        AND CMAKE_CXX_COMPILER_VERSION VERSION_LESS "7")
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC"       AND CMAKE_CXX_COMPILER_VERSION VERSION_LESS "19.14")
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "Clang"      AND CMAKE_CXX_COMPILER_VERSION VERSION_LESS "6")
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang" AND CMAKE_CXX_COMPILER_VERSION VERSION_LESS "10.0")
else()
  # only if c++17 supported
  message("** The compiler supports C++17")
  add_subdirectory(empty)
  add_subdirectory(sqlite3)
endif()

set(TEST_NAME main.tests)
add_executable(${TEST_NAME} main.test.cpp )

target_compile_features(${TEST_NAME} PRIVATE cxx_std_11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
conan_target_link_libraries(${TEST_NAME} ${CONAN_LIBS})

message("-- Conan libs: ${CONAN_LIBS}")

enable_testing()
add_test(NAME ${TEST_NAME}
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND ${TEST_NAME})
