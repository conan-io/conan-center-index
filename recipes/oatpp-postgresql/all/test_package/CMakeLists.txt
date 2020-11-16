cmake_minimum_required(VERSION 3.1)
project(oatpp-postgresql-test CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(oatpp-postgresql REQUIRED)

add_executable(oatpp-postgresql-test oatpp-postgresql-test.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
target_link_libraries(oatpp-postgresql-test PRIVATE oatpp::oatpp-postgresql)
