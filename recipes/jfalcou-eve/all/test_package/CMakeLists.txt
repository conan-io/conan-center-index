cmake_minimum_required(VERSION 3.12)
project(test_package)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(eve REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} eve::eve)
# FIXME: recipe should transitively sets proper minimum cxx standard.
# See https://github.com/conan-io/conan/issues/7772 about revising cxx std model.
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 20)
