cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

include(FindPkgConfig)

pkg_check_modules(OsiClp REQUIRED IMPORTED_TARGET osi-clp)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::OsiClp)
