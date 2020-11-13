cmake_minimum_required(VERSION 3.1)
project(oatpp-sqlite-test CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(oatpp-sqlite REQUIRED)

add_executable(oatpp-sqlite-test oatpp-sqlite-test.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)

target_link_libraries(oatpp-sqlite-test PRIVATE oatpp::oatpp-sqlite)
