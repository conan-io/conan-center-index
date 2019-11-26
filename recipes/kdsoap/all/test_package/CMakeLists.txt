cmake_minimum_required(VERSION 3.0)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Qt5Core REQUIRED)
find_package(Qt5Network REQUIRED)

add_executable(kdsoap_test main.cpp)
target_link_libraries(kdsoap_test Qt5::Core ${CONAN_LIBS})

