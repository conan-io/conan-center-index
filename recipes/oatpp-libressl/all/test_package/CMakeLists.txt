cmake_minimum_required(VERSION 3.1)
project(oatpp-libressl-test CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(oatpp-libressl REQUIRED)

add_executable(oatpp-libressl-test oatpp-libressl-test.cpp)
target_link_libraries(oatpp-libressl-test PRIVATE oatpp::oatpp-libressl)
