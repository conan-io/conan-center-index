cmake_minimum_required(VERSION 3.1)
project(oatpp-swagger-test CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(oatpp-swagger REQUIRED)

add_executable(oatpp-swagger-test oatpp-swagger-test.cpp)

set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)

target_link_libraries(oatpp-swagger-test PRIVATE oatpp::oatpp-swagger)
