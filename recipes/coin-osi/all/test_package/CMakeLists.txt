cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

include(FindPkgConfig)

pkg_check_modules(OsiUnitTests REQUIRED IMPORTED_TARGET osi-unittests)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::OsiUnitTests)
