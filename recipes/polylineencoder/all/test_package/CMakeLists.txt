cmake_minimum_required(VERSION 3.12)

project(polylineencoder_test)
set (CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(poly_test
  test_package.cpp
)

target_link_libraries(poly_test
  ${CONAN_LIBS}
)

enable_testing()
add_test(NAME Test COMMAND poly_test)
